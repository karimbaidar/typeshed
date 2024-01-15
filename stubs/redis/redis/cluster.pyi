from _typeshed import Incomplete, Unused
from collections.abc import Callable, Iterable, Sequence
from threading import Lock
from types import TracebackType
from typing import Any, ClassVar, Literal, NoReturn, Protocol
from typing_extensions import Self

from redis.client import CaseInsensitiveDict, PubSub, Redis, _ParseResponseOptions
from redis.commands import CommandsParser, RedisClusterCommands
from redis.commands.core import _StrType
from redis.connection import BaseParser, Connection, ConnectionPool, Encoder, _ConnectionPoolOptions, _Encodable
from redis.exceptions import MovedError, RedisError
from redis.retry import Retry
from redis.typing import EncodableT

def get_node_name(host: str, port: str | int) -> str: ...
def get_connection(redis_node: Redis[Any], *args, **options: _ConnectionPoolOptions) -> Connection: ...
def parse_scan_result(command: Unused, res, **options): ...
def parse_pubsub_numsub(command: Unused, res, **options: Unused): ...
def parse_cluster_slots(resp, **options) -> dict[tuple[int, int], dict[str, Any]]: ...
def parse_cluster_myshardid(resp: bytes, **options: Unused) -> str: ...

PRIMARY: str
REPLICA: str
SLOT_ID: str
REDIS_ALLOWED_KEYS: tuple[str, ...]
KWARGS_DISABLED_KEYS: tuple[str, ...]
PIPELINE_BLOCKED_COMMANDS: tuple[str, ...]

def cleanup_kwargs(**kwargs: Any) -> dict[str, Any]: ...

# It uses `DefaultParser` in real life, but it is a dynamic base class.
class ClusterParser(BaseParser): ...

class AbstractRedisCluster:
    RedisClusterRequestTTL: ClassVar[int]
    PRIMARIES: ClassVar[str]
    REPLICAS: ClassVar[str]
    ALL_NODES: ClassVar[str]
    RANDOM: ClassVar[str]
    DEFAULT_NODE: ClassVar[str]
    NODE_FLAGS: ClassVar[set[str]]
    COMMAND_FLAGS: ClassVar[dict[str, str]]
    CLUSTER_COMMANDS_RESPONSE_CALLBACKS: ClassVar[dict[str, Any]]
    RESULT_CALLBACKS: ClassVar[dict[str, Callable[[Incomplete, Incomplete], Incomplete]]]
    ERRORS_ALLOW_RETRY: ClassVar[tuple[type[RedisError], ...]]

class RedisCluster(AbstractRedisCluster, RedisClusterCommands[_StrType]):
    user_on_connect_func: Callable[[Connection], object] | None
    encoder: Encoder
    cluster_error_retry_attempts: int
    command_flags: dict[str, str]
    node_flags: set[str]
    read_from_replicas: bool
    reinitialize_counter: int
    reinitialize_steps: int
    nodes_manager: NodesManager
    cluster_response_callbacks: CaseInsensitiveDict[str, Callable[..., Incomplete]]
    result_callbacks: CaseInsensitiveDict[str, Callable[[Incomplete, Incomplete], Incomplete]]
    commands_parser: CommandsParser
    def __init__(  # TODO: make @overloads, either `url` or `host:port` can be passed
        self,
        host: str | None = None,
        port: int | None = 6379,
        startup_nodes: list[ClusterNode] | None = None,
        cluster_error_retry_attempts: int = 3,
        retry: Retry | None = None,
        require_full_coverage: bool = False,
        reinitialize_steps: int = 5,
        read_from_replicas: bool = False,
        dynamic_startup_nodes: bool = True,
        url: str | None = None,
        address_remap: Callable[[str, int], tuple[str, int]] | None = None,
        **kwargs,
    ) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(
        self, type: type[BaseException] | None, value: BaseException | None, traceback: TracebackType | None
    ) -> None: ...
    def __del__(self) -> None: ...
    def disconnect_connection_pools(self) -> None: ...
    @classmethod
    def from_url(cls, url: str, **kwargs) -> Self: ...
    def on_connect(self, connection: Connection) -> None: ...
    def get_redis_connection(self, node: ClusterNode) -> Redis[Any]: ...
    def get_node(
        self, host: str | None = None, port: str | int | None = None, node_name: str | None = None
    ) -> ClusterNode | None: ...
    def get_primaries(self) -> list[ClusterNode]: ...
    def get_replicas(self) -> list[ClusterNode]: ...
    def get_random_node(self) -> ClusterNode: ...
    def get_nodes(self) -> list[ClusterNode]: ...
    def get_node_from_key(self, key: _Encodable, replica: bool = False) -> ClusterNode | None: ...
    def get_default_node(self) -> ClusterNode | None: ...
    def set_default_node(self, node: ClusterNode | None) -> bool: ...
    def monitor(self, target_node: Incomplete | None = None): ...
    def pubsub(
        self, node: Incomplete | None = None, host: Incomplete | None = None, port: Incomplete | None = None, **kwargs
    ): ...
    def pipeline(self, transaction: Incomplete | None = None, shard_hint: Incomplete | None = None): ...
    def lock(
        self,
        name: str,
        timeout: float | None = None,
        sleep: float = 0.1,
        blocking: bool = True,
        blocking_timeout: float | None = None,
        lock_class: type[Incomplete] | None = None,
        thread_local: bool = True,
    ): ...
    def keyslot(self, key: _Encodable) -> int: ...
    def determine_slot(self, *args): ...
    def get_encoder(self) -> Encoder: ...
    def get_connection_kwargs(self) -> dict[str, Any]: ...
    def execute_command(self, *args, **kwargs): ...
    def close(self) -> None: ...

class ClusterNode:
    host: str
    port: int
    name: str
    server_type: str | None
    redis_connection: Redis[Incomplete] | None
    def __init__(
        self, host: str, port: int, server_type: str | None = None, redis_connection: Redis[Incomplete] | None = None
    ) -> None: ...
    def __eq__(self, obj: object) -> bool: ...
    def __del__(self) -> None: ...

class LoadBalancer:
    primary_to_idx: dict[str, int]
    start_index: int
    def __init__(self, start_index: int = 0) -> None: ...
    def get_server_index(self, primary: str, list_size: int) -> int: ...
    def reset(self) -> None: ...

class NodesManager:
    nodes_cache: dict[str, ClusterNode]
    slots_cache: dict[str, list[ClusterNode]]
    startup_nodes: dict[str, ClusterNode]
    default_node: ClusterNode | None
    from_url: bool
    connection_pool_class: type[ConnectionPool]
    connection_kwargs: dict[str, Incomplete]  # TODO: could be a TypedDict
    read_load_balancer: LoadBalancer
    address_remap: Callable[[str, int], tuple[str, int]] | None
    def __init__(
        self,
        startup_nodes: Iterable[ClusterNode],
        from_url: bool = False,
        require_full_coverage: bool = False,
        lock: Lock | None = None,
        dynamic_startup_nodes: bool = True,
        connection_pool_class: type[ConnectionPool] = ...,
        address_remap: Callable[[str, int], tuple[str, int]] | None = None,
        **kwargs,  # TODO: same type as connection_kwargs
    ) -> None: ...
    def get_node(
        self, host: str | None = None, port: int | str | None = None, node_name: str | None = None
    ) -> ClusterNode | None: ...
    def update_moved_exception(self, exception: MovedError) -> None: ...
    def get_node_from_slot(self, slot: str, read_from_replicas: bool = False, server_type: str | None = None) -> ClusterNode: ...
    def get_nodes_by_server_type(self, server_type: str) -> list[ClusterNode]: ...
    def populate_startup_nodes(self, nodes: Iterable[ClusterNode]) -> None: ...
    def check_slots_coverage(self, slots_cache: dict[str, list[ClusterNode]]) -> bool: ...
    def create_redis_connections(self, nodes: Iterable[ClusterNode]) -> None: ...
    def create_redis_node(self, host: str, port: int | str, **kwargs: Any) -> Redis[Incomplete]: ...
    def initialize(self) -> None: ...
    def close(self) -> None: ...
    def reset(self) -> None: ...
    def remap_host_port(self, host: str, port: int) -> tuple[str, int]: ...

class ClusterPubSub(PubSub):
    node: ClusterNode | None
    cluster: RedisCluster[Any]
    def __init__(
        self,
        redis_cluster: RedisCluster[Any],
        node: ClusterNode | None = None,
        host: str | None = None,
        port: int | None = None,
        **kwargs,
    ) -> None: ...
    def set_pubsub_node(
        self, cluster: RedisCluster[Any], node: ClusterNode | None = None, host: str | None = None, port: int | None = None
    ) -> None: ...
    def get_pubsub_node(self) -> ClusterNode | None: ...
    def execute_command(self, *args, **kwargs) -> None: ...
    def get_redis_connection(self) -> Redis[Any] | None: ...

class ClusterPipeline(RedisCluster[_StrType]):
    command_stack: list[Incomplete]
    nodes_manager: Incomplete
    refresh_table_asap: bool
    result_callbacks: Incomplete
    startup_nodes: Incomplete
    read_from_replicas: bool
    command_flags: Incomplete
    cluster_response_callbacks: Incomplete
    cluster_error_retry_attempts: int
    reinitialize_counter: int
    reinitialize_steps: int
    encoder: Encoder
    commands_parser: Incomplete
    def __init__(
        self,
        nodes_manager,
        commands_parser,
        result_callbacks: Incomplete | None = None,
        cluster_response_callbacks: Incomplete | None = None,
        startup_nodes: Incomplete | None = None,
        read_from_replicas: bool = False,
        cluster_error_retry_attempts: int = 3,
        reinitialize_steps: int = 5,
        lock: Lock | None = None,
        **kwargs,
    ) -> None: ...
    def __len__(self) -> int: ...
    def __bool__(self) -> Literal[True]: ...
    def execute_command(self, *args, **kwargs): ...
    def pipeline_execute_command(self, *args, **options): ...
    def raise_first_error(self, stack) -> None: ...
    def annotate_exception(self, exception, number, command) -> None: ...
    def execute(self, raise_on_error: bool = True): ...
    scripts: set[Any]  # is only set in `reset()`
    watching: bool  # is only set in `reset()`
    explicit_transaction: bool  # is only set in `reset()`
    def reset(self) -> None: ...
    def send_cluster_commands(self, stack, raise_on_error: bool = True, allow_redirections: bool = True): ...
    def eval(self) -> None: ...
    def multi(self) -> None: ...
    def immediate_execute_command(self, *args, **options) -> None: ...
    def load_scripts(self) -> None: ...
    def watch(self, *names) -> None: ...
    def unwatch(self) -> None: ...
    def script_load_for_pipeline(self, *args, **kwargs) -> None: ...
    def delete(self, *names): ...

def block_pipeline_command(name: str) -> Callable[..., NoReturn]: ...

class PipelineCommand:
    args: Sequence[EncodableT]
    options: _ParseResponseOptions
    position: int | None
    result: Any | Exception | None
    node: Incomplete | None
    asking: bool
    def __init__(
        self, args: Sequence[EncodableT], options: _ParseResponseOptions | None = None, position: int | None = None
    ) -> None: ...

class _ParseResponseCallback(Protocol):
    def __call__(self, __connection: Connection, __command: EncodableT, **kwargs: Incomplete) -> Any: ...

class NodeCommands:
    parse_response: _ParseResponseCallback
    connection_pool: ConnectionPool
    connection: Connection
    commands: list[PipelineCommand]
    def __init__(
        self, parse_response: _ParseResponseCallback, connection_pool: ConnectionPool, connection: Connection
    ) -> None: ...
    def append(self, c: PipelineCommand) -> None: ...
    def write(self) -> None: ...
    def read(self) -> None: ...
