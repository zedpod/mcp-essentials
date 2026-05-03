"""sitepulse MCP server. Run: python -m sitepulse"""

from mcp.server.fastmcp import FastMCP

from sitepulse.core import inspect as core_inspect

mcp = FastMCP("orzed-sitepulse")


@mcp.tool()
def inspect(
    domain: str,
    checks: list[str] | None = None,
    language: str = "en",
    timeout_seconds: float = 6.0,
) -> dict:
    """DNS, RDAP, TLS, and HTTP health snapshot for a domain.

    Args:
        domain: Hostname or full URL.
        checks: Subset of ["dns","rdap","ssl","http"]. None runs all four.
        language: en/tr.
        timeout_seconds: Per-check timeout.
    """
    return core_inspect(
        domain, checks=checks, language=language, timeout_seconds=timeout_seconds
    ).model_dump(mode="json")


if __name__ == "__main__":
    mcp.run()
