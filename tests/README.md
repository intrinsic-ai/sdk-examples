# CI/CD journey

This guide shows how to setup and run the `flowstate-ci.yml` Github action.

## Overview

This journey guides you into several `inctl` commands in order to go through an end to end test. For testing purposes, it will uses the same [sdk-examples](https://github.com/intrinsic-ai/sdk-examples) repo as the base. In that way it will use the following skills: `//skills/start_stopwatch:start_stopwatch_skill`,`//skills/stop_stopwatch:stop_stopwatch_py_skill` and the service `//services/stopwatch:stopwatch_service`.

## Setup

1. Add the `INTRINSIC_API_KEY` from `inctl auth login` as a secret on Github: Before starting the task, you'll need to add your own `INTRINSIC_API_KEY` as a Github secret. This one expires in 90 days and you can use it during this time while you don't generate a new one. You can follow [this guide](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets#creating-secrets-for-a-repository) in order to create the secret.

2. Decide in which organization you will test: get your organization between *intrinsic@intrinsic-prod-us*, *intrinsic@intrinsic-dev* or *intrinsic@giza-workcells*.

3. Get your solution id: If you don't have a solution created in your prefered organization where you want to test the workflow, create a new one following [this guide](https://flowstate.intrinsic.ai/docs/guides/build_with_flowstate/create_a_new_solution/). Then, copy the solution ID.

4. Decide which version of Intrinsic tools you will use: by default the version is the *latest*.

## Running the workflow

> [!NOTE]
> Before running the action, your solution **must be started** in your desired organization.

The worklow contains one main bash script which is an end-to-end journey for performing continuous integration. This bash goes through the following steps:

1. Check Intrinsic Organization.
2. Deploy an existing solution.
3. Build the skill(s).
4. Install the skill(s).
5. Build the service(s).
6. Install the service(s).
7. Add the service(s).
8. Add a process that uses the skill and service.

For running the github action:

1. Go to the *Actions* tab on the sdk-examples repo.
2. On the left panel called *Actions*, click on the **Flowstate CI**
3. Go to the main panel at the middle and click on the upper right corner *Run workflow*.
4. When you click *Run workflow* it will display three spaces: Flowstate Solution ID, Flowstate Organization and Version of Intrinsic tools to use. Fill every gap with your desired input that you get from the setup.
5. Click on the green button *Run worflow* at the bottom of the options displayed before.

The above steps are shown in the following image:

![Runing the action: steps](./images/action_steps.png)

If you want to run it locally, you can do it with the following command from the `sdk-examples` directory:

```bash
. ./tests/run_ci.sh --skill=skills/start_stopwatch:start_stopwatch_skill,skills/stop_stopwatch:stop_stopwatch_py_skill --org=intrinsic@intrinsic-prod-us --solution=example_APPLIC --service=services/stopwatch:stopwatch_service
```

Recall that for this locally run you will need to have your `INTRINSIC_API_KEY` stored on your `.bashrc` as an environment variable.
