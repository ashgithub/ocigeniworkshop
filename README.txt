1. setup vscode &  python 3.11.5
    - pip install oci
    - pip install oracledb
    - run AISandboxEnvCheck.py 

2. Once you get access to cloud.oracle.com, tennacy: igiuhubdevoc1 
    1. set up your api key  (task1 at https://oracle-livelabs.github.io/apex/ai-vision-lab/workshops/tenancy/index.html?lab=1-configure-oci#Task1:GenerateAPIKeysusingOCIConsole
    2. set up .oci/config. Create a new section cand [AISANDBOX]
    3. download wallet and setup sql developer ( click on database connection here : https://cloud.oracle.com/db/adbs/ocid1.autonomousdatabase.oc1.phx.anyhqljsghwivzaajq6pzddmo4xbv5dtaytd2ctybjathmhcymf4vumagioa?region=null)

4. setup your sanbox.json file 

3. oci commands to clean : 
   - oci os object bulk-delete -ns axaemuxiyife -bn workshopbucket --prefix AAGARWA/ --include ocid1\*
   - oci os object list --all --fields name,timeCreated --bucket-name=workshopbucket | grep AAGARWA
   - oci os object put -bn workshopbucket --file test.txt
