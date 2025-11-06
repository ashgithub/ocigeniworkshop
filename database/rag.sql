-- if you have errors running sample code reach out for help in #igiu-ai-learning
-- #igiu-innovation-lab: discuss project ideas 
-- #adb-select-ai-users : questions about oracle 23ai select ai 

BEGIN
dbms_cloud_ai.drop_profile(
    profile_name => 'ocirag',
    force => true
    );
END;
/


BEGIN
       DBMS_CLOUD_AI.DROP_VECTOR_INDEX(
         index_name  => 'RAG_INDEX');
END;
/

BEGIN
DBMS_CLOUD_AI.CREATE_PROFILE (
        profile_name => 'ocirag',        
        attributes => '{
            "provider": "oci",
             "credential_name": "OCI_GENAI_CRED",
            "model":"meta.llama-4-scout-17b-16e-instruct",
             "vector_index_name": "RAG_INDEX"
           
            }'
        );
end;
/

begin
  dbms_cloud_ai.set_profile(
        profile_name => 'ocirag'
    );
end;
/

-- load files in the OB bucket. change the location to the bucket/folder you created
BEGIN
       DBMS_CLOUD_AI.CREATE_VECTOR_INDEX(
         index_name  => 'RAG_INDEX',
         attributes  => '{"vector_db_provider": "oracle",
                          "location": "https://objectstorage.us-phoenix-1.oraclecloud.com/n/axaemuxiyife/b/workshopbucket/o/AAGARWA/kb-test/",
                          "object_storage_credential_name": "OCI_GENAI_CRED",
                          "profile_name": "ocirag",
                          "vector_dimension": 1024,
                          "vector_distance_metric": "cosine",
                          "chunk_overlap":128,
                          "chunk_size":1024
      }');
     END;
     /
     
     
begin
  dbms_cloud_ai.set_profile(
        profile_name => 'ocirag'
    );
end;
/

set pages 100
set linesizes 150
select ai  narrate tell me about France

select ai  narrate tell me three thnings about  Pope Pius XII
-- troiubleshootiung --
select * from user_cloud_pipeline_history
select * from USER_CLOUD_PIPELINES
select * from USER_LOAD_OPERATIONS
select job_name, error#, errors from DBA_SCHEDULER_RUNNING_JOBS where job_name like 'PIPELINE%';
    select *  from RAG_INDEX$VECTAB