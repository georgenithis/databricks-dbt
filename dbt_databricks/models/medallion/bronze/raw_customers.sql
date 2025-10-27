{{
    config(
        materialized = 'incremental',
        schema = 'bronze',
        tags = ["ingestion"]
    )    
}}


WITH RankedEmployees AS (
    SELECT  EMP.NAME,
            EMP.EMP_ID,
            EMP.SALARY,
            DEPT.DEPT_NAME,
            ROW_NUMBER() OVER(PARTITION BY EMP.DEPT_ID ORDER BY EMP.SALARY DESC) as SalaryRank
    FROM    Employees AS EMP
    JOIN    Departments AS DEPT
    ON      EMP.DEPT_ID = DEPT.DEPT_ID
)
    SELECT  NAME, 
            EMP_ID, 
            SALARY, 
            DEPT_NAME
    FROM    RankedEmployees
    WHERE   SalaryRank = 1
    ORDER BY 
            SALARY DESC