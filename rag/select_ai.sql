

--https://docs.oracle.com/en-us/iaas/autonomous-database-serverless/doc/select-ai-examples.html#GUID-2FBD7DDB-CAC3-47AF-AB66-17F44C2ADAA4
SELECT USER FROM DUAL;

BEGIN
dbms_cloud_ai.drop_profile(
    profile_name => 'genaish',
    force => true
    );
END;
/

BEGIN
DBMS_CLOUD_AI.CREATE_PROFILE (
        profile_name => 'genaish',        
        attributes => '{
            "provider": "oci",
             "credential_name": "OCI_GENAI_CRED",
            "model":"meta.llama-3.1-70b-instruct",
            "comments":"true",            
            "object_list": [{"owner": "SH"}]
            }'
        );
end;
/

begin
  dbms_cloud_ai.set_profile(
        profile_name => 'genaish'
    );
end;
/

set wrap on


select ai how many customers exist;
select ai runsql  narrate how many customers exist;
select ai showsql  narrate how many customers exist;
select ai explainsql  narrate how many customers exist;
select ai narrate how many customers exist;
select ai chat how many customers exist;
select ai chat why is sky blue
select ai showsql how many customers in San Francisco are married;

select ai find top3 baby boomer big spenders
select ai showsql find top3 baby boomer big spenders



SELECT * FROM ( SELECT "CUST_FIRST_NAME", "CUST_LAST_NAME", "CUST_INCOME_LEVEL", "CUST_YEAR_OF_BIRTH", SUM("AMOUNT_SOLD") AS "TOTAL_SPENT" FROM "SH"."CUSTOMERS" "C" INNER JOIN "SH"."SALES" "S" ON "C"."CUST_ID" = "S"."CUST_ID" WHERE "CUST_YEAR_OF_BIRTH" BETWEEN 1946 AND 1964 GROUP BY "CUST_FIRST_NAME", "CUST_LAST_NAME", "CUST_INCOME_LEVEL", "CUST_YEAR_OF_BIRTH" ORDER BY SUM("AMOUNT_SOLD") DESC ) WHERE ROWNUM <= 3