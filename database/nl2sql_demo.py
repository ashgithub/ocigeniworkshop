"""
What this file does:
Demonstrates Natural-Language-to-SQL (NL2SQL) conversion using OCI Generative AI. It translates plain English questions into SQL queries that execute against the SH (Sales History) schema in Oracle Database, displaying results in a formatted table.

Documentation to reference:
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- Oracle DB: https://docs.oracle.com/en/database/oracle/oracle-database/23/
- Python-oracledb: https://python-oracledb.readthedocs.io/
- OCI Python SDK: https://github.com/oracle/oci-python-sdk/tree/master/src/oci/generative_ai_inference/models

Relevant slack channels:
- #generative-ai-users: for questions on OCI Gen AI
- #igiu-innovation-lab: general discussions on your project
- #igiu-ai-learning: help with sandbox environment or help with running this code

Env setup:
- sandbox.yaml: Contains OCI config, compartment, DB details, and wallet path.
- .env: Load environment variables (e.g., API keys if needed).

How to run the file:
uv run database/nl2sql_demo.py

Comments to important sections of file:
- Step 1: Load config and initialize OCI client.
- Step 2: Set up database connection.
- Step 3: Build chat prompt with schema description and examples.
- Step 4: Interactive query loop with LLM-generated SQL.
- Step 5: Execute SQL and display results.
"""

from __future__ import annotations

import os
import sys
import textwrap
from typing import List

from dotenv import load_dotenv
from envyaml import EnvYAML
import oracledb
import oci
from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import (
    GenericChatRequest,
    ChatDetails,
    OnDemandServingMode,
    BaseChatRequest,
    UserMessage,
    SystemMessage,
    TextContent,
)

# ------------------------------------------------------------------------------
# Utility helpers (standard-library only)
# ------------------------------------------------------------------------------


def hr(title: str = "", width: int = 80, char: str = "-") -> None:
    """Print a horizontal rule, optionally with a centred title."""
    if title:
        pad = (width - len(title) - 2) // 2
        print(char * pad, f" {title} ", char * (width - len(title) - 2 - pad), sep="")
    else:
        print(char * width)


def pretty_table(cols: List[str], rows: List[tuple]) -> None:
    """Print a list-of-tuples as a simple ASCII table."""
    # Compute column widths
    widths = [len(str(c)) for c in cols]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    # Build format strings
    row_fmt = " | ".join(f"{{:<{w}}}" for w in widths)
    sep = "-+-".join("-" * w for w in widths)

    # Header
    print(row_fmt.format(*cols))
    print(sep)
    # Rows
    for row in rows:
        print(row_fmt.format(*[str(x) for x in row]))


# ------------------------------------------------------------------------------
# Config and credentials
# ------------------------------------------------------------------------------

SANDBOX_CONFIG_FILE = "sandbox.yaml"
#MODEL_ID = "meta.llama-4-scout-17b-16e-instruct"
MODEL_ID = "xai.grok-4-fast-reasoning"

LLM_ENDPOINT = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

load_dotenv()  # expand ${VAR} placeholders inside YAML

try:
    cfg = EnvYAML(SANDBOX_CONFIG_FILE)
except FileNotFoundError:
    print(f"ERROR: Cannot find {SANDBOX_CONFIG_FILE}")
    sys.exit(1)

# OCI credentials
OCI_CONFIG_PATH = os.path.expanduser(cfg["oci"]["configFile"])
OCI_PROFILE = cfg["oci"]["profile"]
OCI_COMPARTMENT_ID = cfg["oci"]["compartment"]

# Database credentials
db_cfg = cfg["db"]
DB_DSN = db_cfg["dsn"]
DB_USER = db_cfg["username"]
DB_PASSWORD = db_cfg["password"]
DB_WALLET_PATH = os.path.expanduser(db_cfg["walletPath"])
DB_WALLET_PASS = db_cfg["walletPass"]


# ------------------------------------------------------------------------------
# Prompt engineering
# ------------------------------------------------------------------------------

SCHEMA_DESCRIPTION = textwrap.dedent(
    """
    You are an expert Oracle SQL generator. The user asks questions about
    the SH (Sales History) schema which contains:

      • COUNTRIES(country_id, country_name, region_id)
      • CUSTOMERS(cust_id, cust_first_name, cust_last_name, cust_gender,
                  cust_year_of_birth, country_id, cust_income_level)
      • PRODUCTS(prod_id, prod_name, prod_category, prod_subcategory)
      • CHANNELS(channel_id, channel_desc)
      • TIMES(time_id, calendar_year, calendar_month_desc, calendar_date)
      • SALES(prod_id, cust_id, time_id, channel_id, quantity_sold, amount_sold)

    Joins:
      CUSTOMERS.country_id = COUNTRIES.country_id
      SALES.cust_id        = CUSTOMERS.cust_id
      SALES.prod_id        = PRODUCTS.prod_id
      SALES.channel_id     = CHANNELS.channel_id
      SALES.time_id        = TIMES.time_id

    Always prefix tables with SH. Return valid SQL only. Your output will be directly fed to the oracle database.
    dont include backquotes as they would interfere
    """
)

FEW_SHOT_EXAMPLES = [
    {
        "q": "How many customers are there?",
        "sql": "SELECT COUNT(*) AS customer_cnt FROM SH.CUSTOMERS;",
    },
    {
        "q": "Total amount sold in 1999?",
        "sql": (
            "SELECT SUM(amount_sold) AS total_amount\n"
            "FROM SH.SALES s JOIN SH.TIMES t ON s.time_id = t.time_id\n"
            "WHERE t.calendar_year = 1999;"
        ),
    },
    {
        "q": "Top 3 products by quantity sold in 2000",
        "sql": (
            "SELECT p.prod_name, SUM(quantity_sold) qty\n"
            "FROM SH.SALES s JOIN SH.PRODUCTS p ON s.prod_id = p.prod_id\n"
            "JOIN SH.TIMES t ON s.time_id = t.time_id\n"
            "WHERE t.calendar_year = 2000\n"
            "GROUP BY p.prod_name\n"
            "ORDER BY qty DESC FETCH FIRST 3 ROWS ONLY;"
        ),
    },
]


def build_chat_details(question: str) -> ChatDetails:
    sys_msg = SystemMessage(
        content=[
            TextContent(
                text=SCHEMA_DESCRIPTION
                + "\n\n"
                + "\n\n".join(f"Q: {ex['q']}\nSQL:\n{ex['sql']}" for ex in FEW_SHOT_EXAMPLES)
            )
        ]
    )
    user_msg = UserMessage(content=[TextContent(text=question)])

    chat_req = GenericChatRequest(
        messages=[sys_msg, user_msg],
        api_format=BaseChatRequest.API_FORMAT_GENERIC,
        max_tokens=400,
        temperature=0.2,
        num_generations=1,
        is_stream=False,
    )

    return ChatDetails(
        serving_mode=OnDemandServingMode(model_id=MODEL_ID),
        compartment_id=OCI_COMPARTMENT_ID,
        chat_request=chat_req,
    )


# ------------------------------------------------------------------------------
# DB helpers
# ------------------------------------------------------------------------------


def connect_db() -> oracledb.Connection:
    return oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=DB_DSN,
        config_dir=DB_WALLET_PATH,
        wallet_location=DB_WALLET_PATH,
        wallet_password=DB_WALLET_PASS,

    )


def execute_query(conn: oracledb.Connection, sql: str):
    """Execute SQL query and return column names and rows."""
    with conn.cursor() as cur:
        cur.execute(sql)
        return [d[0] for d in cur.description], cur.fetchall()


# ------------------------------------------------------------------------------
# Main program
# ------------------------------------------------------------------------------


def main() -> None:
    hr("NL → SQL Demo")

    # OCI client
    try:
        oci_config = oci.config.from_file(OCI_CONFIG_PATH, OCI_PROFILE)
    except Exception as exc:
        print(f"ERROR: Cannot load OCI config: {exc}")
        sys.exit(1)

    llm_client = GenerativeAiInferenceClient(
        config=oci_config,
        service_endpoint=LLM_ENDPOINT,
        retry_strategy=oci.retry.NoneRetryStrategy(),
        timeout=(10, 240),
    )

    # DB connection
    try:
        conn = connect_db()
    except oracledb.Error as exc:
        print(f"ERROR: DB connection failed: {exc}")
        sys.exit(1)

    print("Enter a natural-language question (blank to exit).")
    while True:
        try:
            question = input("\n> ").strip()
        except KeyboardInterrupt:
            print("\nExiting.")
            break
        if not question:
            break

        details = build_chat_details(question)
        try:
            resp = llm_client.chat(details)
            generated_sql = resp.data.chat_response.choices[0].message.content[0].text.strip()
        except Exception as exc:
            print(f"ERROR: LLM failure: {exc}")
            continue

        hr("Generated SQL")
        print(generated_sql)

        try:
            cols, rows = execute_query(conn, generated_sql)
        except oracledb.Error as exc:
            print(f"ERROR: SQL execution failed: {exc}")
            continue

        hr("Query Result")
        pretty_table(cols, rows)

    conn.close()
    hr("Done")


if __name__ == "__main__":
    main()
