#!/bin/bash
meltano install loader target-postgres
meltano install transformer dbt-postgres
meltano install extractor tap-csv