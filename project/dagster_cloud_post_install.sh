#!/bin/bash
echo "hello world"
meltano install loader target-postgres
meltano install transformer dbt-postgres
meltano install extractor tap-csv