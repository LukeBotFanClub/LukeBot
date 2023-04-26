import logging
from abc import ABC, abstractmethod
from json import JSONDecodeError
from typing import Any, Type

import aiohttp

from .settings import settings

logger = logging.getLogger(__name__)

TOKEN: str = settings.GG_TOKEN


class GraphQLObject(ABC):
    def __init__(
        self,
        item,
        *args,
        **kwargs,
    ):
        self.parent = kwargs.pop("parent")
        self.key = kwargs.pop("key")
        if item is None:
            arg = []
        else:
            arg = [item]
        super().__init__(*arg, *args, **kwargs)

    @classmethod
    @abstractmethod
    def _builtin(cls) -> type:
        return object

    def as_builtin(self):
        return self._builtin()(self)


class Null(GraphQLObject):
    @classmethod
    def _builtin(cls) -> type:
        return type(None)

    def __init__(
        self,
        item: None = None,
        /,
        parent: GraphQLObject | None = None,
        key: str | int | None = None,
    ):
        super().__init__(None, parent=parent, key=key)
        self.none = item

    def __getitem__(self, item):
        msg = (
            f"The item at '{self.key}' inside {self.parent} is a null value, "
            f"but was treated as a dict/list using the key '{item}'"
        )
        logger.warning(msg)
        return type(self)(None, parent=self, key=item)

    def as_builtin(self):
        return None

    def __str__(self):
        return "null"

    def __repr__(self):
        return "<GraphQL Null value>"

    def __len__(self):
        return 0


def is_null(item: Any) -> bool:
    return (item is None) or isinstance(item, Null)


class GraphQLData(GraphQLObject, dict):
    @classmethod
    def _builtin(cls) -> type:
        return dict

    def __str__(self):
        return f"GraphQLData({super().__str__()})"

    def __init__(
        self,
        item: dict | None = None,
        /,
        parent: GraphQLObject | None = None,
        key: str | int | None = None,
    ):
        if item is not None:
            new_item = {k: convert_to_graphql_data(v, self, k) for k, v in item.items()}
            arg = [new_item]
        else:
            arg = []
        super().__init__(*arg, parent=parent, key=key)

    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except KeyError:
            logger.warning(f"Could not access key '{item}' in {self}")
            return Null(parent=self, key=item)


class GraphQLArray(GraphQLObject, list):
    @classmethod
    def _builtin(cls) -> type:
        return list

    def __str__(self):
        return f"GraphQLArray({super().__str__()})"

    def __init__(
        self,
        item: list | None = None,
        /,
        parent: GraphQLObject | None = None,
        key: str | int | None = None,
    ):
        if item is not None:
            item = [convert_to_graphql_data(v, self, i) for i, v in enumerate(item)]
            arg = [item]
        else:
            arg = []
        super().__init__(*arg, parent=parent, key=key)

    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except IndexError:
            logger.warning(f"Could not access index '{item}' in {self}")
            return Null(parent=self, key=item)


def convert_to_graphql_data(
    item: dict | list | None,
    parent: GraphQLObject,
    key: str | int,
) -> GraphQLObject | dict | list | None:
    mapping: dict[type, Type[GraphQLObject]] = {
        dict: GraphQLData,
        type(None): Null,
        list: GraphQLArray,
    }
    for BaseType, GQLType in mapping.items():
        if isinstance(item, BaseType):
            return GQLType(item, parent=parent, key=key)
    return item


async def api_query(
    query: str,
    http_args: dict[str, Any] | None = None,
    json_args: dict[str, Any] | None = None,
    **variables,
) -> GraphQLData:
    """Performs a query against the start.gg API, raising an error on a failed
    request."""
    if http_args is None:
        http_args = dict()
    if json_args is None:
        json_args = dict()

    endpoint = "https://api.start.gg/gql/alpha"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    async with aiohttp.ClientSession() as session:
        async with session.post(
            endpoint,
            json=dict(query=query, variables=variables),
            headers=headers,
            **http_args,
        ) as response:
            try:
                response.raise_for_status()
            except aiohttp.ClientResponseError as e:
                try:
                    json_data = []
                    responses = e.history
                    for r in responses:
                        if r is not None:
                            json_data.append(await r.json())
                    logger.warning(json_data)
                except (aiohttp.ContentTypeError, JSONDecodeError):
                    pass
                raise e
            data = await response.json(**json_args)
            logger.debug(f"Query to {endpoint} provided {data}")
            return GraphQLData(data)
