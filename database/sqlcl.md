
# SQLcl Quickstart for OCI AI Workshop

## Download SQLcl

Download the latest SQLcl build using curl:

```bash
curl -o sqlcl-latest.zip https://artifacthub-phx.oci.oraclecorp.com/dbtools-dev-mvn-release/oracle/dbtools/sqlcl/25.2.0/sqlcl-25.2.0.zip
```

## MCP Server Configuration ofr cline 

Example configuration (update the path as needed):

```json
"SQLcl": {
  "command": "/Users/KLRICE/dev/sqlcl/bin/sql",
  "args": ["-mcp"],
  "disabled": false
}
```

## Reference

SQLcl setup and environment instructions (official docs):  
https://docs.oracle.com/en/database/oracle/sql-developer-command-line/25.2/sqcug/preparing-your-environment.html

## Example queries to run in cline

1. Connect to the database using the `aiworkshop` connection and `gpt4.1` model.
2. Find out how many customers are in the database.
3. Draw a graph of customers by age bucket and display it as a chart in an HTML page.
