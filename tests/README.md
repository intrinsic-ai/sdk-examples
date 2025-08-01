# CI journey

This folder contains one main bash script which is an end-to-end journey for performing continuous integration. This bash goes through the following workflows:

1. Check Intrinsic Organization. 
2. Deploy an existing solution.
3. Build the skill(s). 
4. Install the skill(s). 
5. Build the service(s). 
6. Install the service(s). 
7. Add the service(s). 
8. Add a process that uses the skill and service. 

You can run it with the following command from the `sdk-examples` directory: 

```
. ./tests/run_ci.sh --skill=skills/start_stopwatch:start_stopwatch_skill,skills/stop_stopwatch:stop_stopwatch_py_skill --org=intrinsic@intrinsic-prod-us --solution=example_APPLIC --service=services/stopwatch:stopwatch_service_bin
```
