import logging
from abc import ABC, abstractmethod
from json import JSONDecodeError
from typing import Any, Type

import aiohttp

from .settings import settings

logger = logging.getLogger(__name__)

TOKEN: str = settings.GG_TOKEN


class GraphQLObject(ABC):
    @abstractmethod
    def __init__(self, item, parent: "GraphQLObject", key: str | int):  # noqa
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def _builtin(cls) -> type:
        raise NotImplementedError

    def as_builtin(self):
        return self._builtin()(self)


class Null(GraphQLObject):
    @classmethod
    def _builtin(cls) -> type:
        return type(None)

    def __init__(
            self,
            item: None = None,
            parent: GraphQLObject | None = None,
            key: str | int | None = None,
    ):
        self.parent = parent
        self.key = key
        self.none = item

    def __getitem__(self, item):
        msg = (
            f"The item at '{self.key}' inside {self.parent} is a null value, "
            f"but was treated as a dict using the key '{item}'"
        )
        logger.warning(msg)
        raise KeyError(msg)

    def as_builtin(self):
        return None

    def __str__(self):
        return "null"

    def __repr__(self):
        return "<GraphQL Null value>"


def is_null(item: Any) -> bool:
    return (item is None) or isinstance(item, Null)


class GraphQLData(dict, GraphQLObject):
    @classmethod
    def _builtin(cls) -> type:
        return dict

    def __str__(self):
        return f"GraphQLData({super().__str__()})"

    def __init__(self, item: dict | None = None, /, **kwargs):
        if item is not None:
            item = {k: convert_to_graphql_data(v, self, k) for k, v in item.items()}
            arg = [item]
        else:
            arg = []
        super().__init__(*arg, **kwargs)

    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except KeyError:
            logger.warning(f"Could not access key '{item}' in {self}")
            return Null(parent=self, key=item)


class GraphQLArray(list, GraphQLObject):
    @classmethod
    def _builtin(cls) -> type:
        return list

    def __str__(self):
        return f"GraphQLArray({super().__str__()})"

    def __init__(self, item: list | None = None, /, **kwargs):
        if item is not None:
            item = [convert_to_graphql_data(v, self, i) for i, v in enumerate(item)]
            arg = [item]
        else:
            arg = []
        super().__init__(*arg, **kwargs)

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
                            j = await r.json()
                            json_data.append(j)
                    logger.warning(j)
                except (aiohttp.ContentTypeError, JSONDecodeError):
                    pass
                raise e
            data = await response.json(**json_args)
            return GraphQLData(data)
