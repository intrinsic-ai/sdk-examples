# !/bin/bash

echo "---This bash will go through all the CI journey ---"

# Variables setup

INTRINSIC_ORGANIZATION=""
INTRINSIC_VM_DURATION=""
SKILL_BAZEL=""
INTRINSIC_SOLUTION=""
SERVICE_BAZEL=""
ORG=""
service_name=""

echo "--- Processing command line arguments ---"
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --org=*)
            INTRINSIC_ORGANIZATION="${1#*=}"
            echo "Argument --org received: $INTRINSIC_ORGANIZATION"
            ;;
        --vm=*)
            INTRINSIC_VM_DURATION="${1#*=}"
            echo "Argument --vm received: $INTRINSIC_VM_DURATION"
            ;;
        --skill=*)
            SKILL_BAZEL="${1#*=}"
            echo "Argument --skill received: $SKILL_BAZEL (comma-separated if multiple)"
            ;;
        --service=*)
            SERVICE_BAZEL="${1#*=}"
            echo "Argument --service received: $SERVICE_BAZEL (comma-separated if multiple)"
            ;;
        --solution=*)
            INTRINSIC_SOLUTION="${1#*=}"
            echo "Argument --solution received: $INTRINSIC_SOLUTION"
            ;;
        *)
            echo "Warning: Unknown argument ignored: $1"
            ;;
    esac
    shift
done
echo "-----------------------------------"
echo ""

echo "1. Check Intrinsic Organization"

if [ -z "$INTRINSIC_ORGANIZATION" ]; then
    read -p "Please, write your intrinsic org name (e.g. intrinsic@intrinsic-prod-us): " INTRINSIC_ORGANIZATION < /dev/tty
    if [ -z "$INTRINSIC_ORGANIZATION" ]; then
        echo "Error! Org name was not set. Exiting."
        exit 1
    fi
fi
if [[ "$INTRINSIC_ORGANIZATION" == *"@"* ]]; then
    ORG="${INTRINSIC_ORGANIZATION#*@}"
    echo "Intrinsic Organization is ${INTRINSIC_ORGANIZATION}"
else
    ORG="$INTRINSIC_ORGANIZATION"
fi
export INTRINSIC_ORGANIZATION ORG

echo ""

echo "2. Build the skill(s)."
echo "NOTE: You should have a skill created in order to build it in this step."

SKILL_BAZEL=$(echo "$SKILL_BAZEL" | xargs)

if [ -n "$SKILL_BAZEL" ]; then
    SKILL_TARGETS=$(echo "$SKILL_BAZEL" | tr ',' ' ')

    echo "Building all skills with the targets: $SKILL_TARGETS"

    bazel build $SKILL_TARGETS

    if [ $? -ne 0 ]; then
        echo "Error: Bazel build for skills failed. Exiting."
        exit 1
    fi
    echo "Successfully built all skills."
else
    echo "No skill targets were provided. Skipping build step."
fi

echo ""

echo "3. Build the service(s)"
echo "NOTE: You should have a service created in order to build it in this step."

SERVICE_BAZEL=$(echo "$SERVICE_BAZEL" | xargs)

if [ -n "$SERVICE_BAZEL" ]; then
    SERVICE_TARGETS=$(echo "$SERVICE_BAZEL" | tr ',' ' ')

    echo "Building all services with the targets: $SERVICE_TARGETS"

    bazel build $SERVICE_TARGETS

    if [ $? -ne 0 ]; then
        echo "Error: Bazel build for service failed. Exiting."
        exit 1
    fi
    echo "Successfully built all services."
else
    echo "No services targets were provided. Skipping build step."
fi

echo ""

echo "4.Lease a VM"

if [ -n "$INTRINSIC_VM_DURATION" ]; then 
    echo "Requesting VM for $INTRINSIC_VM_DURATION hours..."
    lease_output=$(inctl vm lease --silent -d "${INTRINSIC_VM_DURATION}h" --org "$INTRINSIC_ORGANIZATION")
    lease_status=$? 
    if [ $lease_status -eq 0 ]; then
        echo ""
        echo "VM lease request successful!"
        extracted_vm_instance=$lease_output

        if [ -n "$extracted_vm_instance" ]; then
            VM_INSTANCE="$extracted_vm_instance"
            echo "Auto-captured VM instance ID: $VM_INSTANCE"
            export VM_INSTANCE 
        else
            echo "Warning: Could not auto-capture VM instance ID from command output."
            echo "Output was: $lease_output"
            read -p "Please, copy and paste the VM instance ID to return it later: " VM_INSTANCE < /dev/tty
            if [ -z "$VM_INSTANCE" ]; then
                echo "Warning: VM instance ID was not provided. You will need to return it manually."
            fi
        fi
    else
        echo "There was an error leasing the VM."
        echo "Command output: $lease_output"
        echo "Please, verify the command and its output."
    fi
else
    echo "VM lease skipped due to missing time duration."
fi

echo ""

echo "5. Deploy an existing solution."

echo "5.1. Starting the solution."

if [ -n "$INTRINSIC_SOLUTION" ]; then
    echo "Starting solution '$INTRINSIC_SOLUTION'..."
    (INTRINSIC_SOLUTION="" inctl solution start "$INTRINSIC_SOLUTION" --org "$INTRINSIC_ORGANIZATION" --cluster "$lease_output")

    timeout_seconds=300 # 5 minutes
    check_interval_seconds=10 
    elapsed_seconds=0

    while true; do
        status_output=$(inctl solution get "$INTRINSIC_SOLUTION" --org "$INTRINSIC_ORGANIZATION")

        if echo "$status_output" | grep -q "is running"; then
            echo "Solution '$INTRINSIC_SOLUTION' is now running."
            break 
        fi

        # Check for timeout
        if [ "$elapsed_seconds" -ge "$timeout_seconds" ]; then
            echo "Error: Timed out after $timeout_seconds seconds."
            echo "Last status check output:"
            echo "$status_output"
            exit 1
        fi

        echo "Not ready yet. Retrying in $check_interval_seconds seconds."
        sleep "$check_interval_seconds"
        elapsed_seconds=$((elapsed_seconds + check_interval_seconds))
    done
    echo "Waiting 3 minutes for the propagation of the solution..."
    sleep 180
else
    echo "Warning: '$INTRINSIC_SOLUTION' is not set. Skipping start and wait logic."
    exit 1
fi

echo ""

echo "6. Install the skill(s)."

INSTALLED_SKILLS=$(inctl skill list --org "$INTRINSIC_ORGANIZATION" --solution "$INTRINSIC_SOLUTION" --filter "sideloaded" 2>&1)

IFS=',' read -ra SKILL_ARRAY <<< "$SKILL_BAZEL"

for SKILL in "${SKILL_ARRAY[@]}"; do
    SKILL=$(echo "$SKILL" | xargs)
    if [ -n "$SKILL" ]; then
        if [[ "$SKILL" == *:* ]]; then
            skill_package="${SKILL%:*}"
            skill_name=$(basename "$skill_package")
            skill_target="${SKILL##*:}"
        else
            echo "Warning: No colon found in SKILL_BAZEL ('$SKILL'). Assuming it's a target within the current package."
            skill_package=""
            skill_target="$SKILL"
        fi

        if echo "$INSTALLED_SKILLS" | grep -q "com.example.${skill_name}"; then
            echo "Skill '$skill_name' is already installed. Removing the skill."
            inctl asset uninstall "com.example.${skill_name}" --org "$INTRINSIC_ORGANIZATION" --solution "$INTRINSIC_SOLUTION"
        fi
        echo "Installing skill: $SKILL"
        inctl skill install bazel-bin/"$skill_package"/"$skill_target".bundle.tar --solution "$INTRINSIC_SOLUTION" --org "$INTRINSIC_ORGANIZATION"
        if [ $? -ne 0 ]; then
            echo "Error: Skill installation for '$SKILL' failed. Exiting."
            exit 1
        fi
    fi
done

echo ""

echo "7. Install the service(s)."

INSTALLED_SERVICES=$(inctl asset list --asset_types="service" --org "$INTRINSIC_ORGANIZATION" --solution "$INTRINSIC_SOLUTION")

IFS=',' read -ra SERVICE_ARRAY <<< "$SERVICE_BAZEL"

for SERVICE in "${SERVICE_ARRAY[@]}"; do
    SERVICE=$(echo "$SERVICE" | xargs)
    if [ -n "$SERVICE" ]; then
        if [[ "$SERVICE" == *:* ]]; then
            service_package="${SERVICE%:*}"
            service_target="${SERVICE##*:}"
        else
            echo "Warning: No colon found in SERVICE ('$SERVICE'). Assuming it's a target within the current package."
            service_package=""
            service_target="$SERVICE"  
        fi

        SERVICES_TARGET+=("$service_target")

        if echo "$INSTALLED_SERVICES" | grep -q "com.example.${service_target}"; then
            echo "Service '$service_target' is already installed. Removing the service."
            inctl service delete "${service_target}" --org "$INTRINSIC_ORGANIZATION" --solution "$INTRINSIC_SOLUTION"
            inctl asset uninstall "com.example.${service_target}" --org "$INTRINSIC_ORGANIZATION" --solution "$INTRINSIC_SOLUTION"
            echo "Waiting for 20 seconds before installing..."
            sleep 20
        fi
        echo "Installing service: $SERVICE"
        inctl service install bazel-bin/"$service_package"/"$service_target".bundle.tar --solution "$INTRINSIC_SOLUTION" --org "$INTRINSIC_ORGANIZATION"


        if [ $? -ne 0 ]; then
            echo "Error: Service installation for '$SERVICE' failed. Exiting."
        fi
    fi
done

echo ""

echo "8. Add the service(s)."

echo "8.1 Listing your installed assets for services"

INSTALLED_SERVICES=()

while IFS= read -r full_service_name; do
    full_service_name=$(echo "$full_service_name" | xargs)

    if [ -z "$full_service_name" ]; then
        continue
    fi

    current_service_target="${full_service_name##*.}"

    found_match=false
    for target in "${SERVICES_TARGET[@]}"; do
        if [ "$current_service_target" == "$target" ]; then
            INSTALLED_SERVICES+=("$full_service_name")
            found_match=true
            echo "Matched and added to INSTALLED_SERVICES: $full_service_name (target: $current_service_target)"
            break
        fi
    done
done < <(inctl asset list --org "$INTRINSIC_ORGANIZATION" --solution "$INTRINSIC_SOLUTION")

echo "8.2 Add the service(s)"

if [ ${#INSTALLED_SERVICES[@]} -eq 0 ]; then
    echo "No matching installed services found to add. Skipping this step."
else
    for i in "${!INSTALLED_SERVICES[@]}"; do
        SERVICE_FULL_NAME="${INSTALLED_SERVICES[$i]}"
        SERVICE_SHORT_NAME="${SERVICES_TARGET[$i]}"

        if [ -n "$SERVICE_FULL_NAME" ] && [ -n "$SERVICE_SHORT_NAME" ]; then
            echo "Adding service '$SERVICE_FULL_NAME' with name '$SERVICE_SHORT_NAME' to solution '$INTRINSIC_SOLUTION'..."
            inctl service add "$SERVICE_FULL_NAME" \
                --org "$INTRINSIC_ORGANIZATION" \
                --solution "$INTRINSIC_SOLUTION" \
                --name "${SERVICE_SHORT_NAME}"

            if [ $? -eq 0 ]; then
                echo "Successfully added service: $SERVICE_FULL_NAME"

            else
                echo "Error: Failed to add service '$SERVICE_FULL_NAME'. Please check the command output."
            fi
        else
            echo "Warning: Skipped adding a service due to empty full name or short name. Full: '$SERVICE_FULL_NAME', Short: '$SERVICE_SHORT_NAME'"
        fi
    done
fi

echo ""
echo "9. Add a process that uses the skill and service."

PYTHON_SCRIPT_PATH="./tests/sbl_ci.py"

echo "Attempting to run the SBL Python script: $PYTHON_SCRIPT_PATH"

if [ ! -f "$PYTHON_SCRIPT_PATH" ]; then
    echo "Error: Python script '$PYTHON_SCRIPT_PATH' not found."
    echo "Please ensure the script exists at the specified path."
    echo "Skipping SBL script execution."
else
    bazel run //tests:sbl_ci -- \
        --org "$INTRINSIC_ORGANIZATION" \
        --solution-id "$INTRINSIC_SOLUTION"
    if [ $? -eq 0 ]; then
        echo "SBL Python script '$PYTHON_SCRIPT_PATH' executed successfully!"
    else
        echo "Error: SBL Python script '$PYTHON_SCRIPT_PATH' failed. Please check its output for details."
    fi
fi

echo ""

echo "10. Stopping your solution"

echo "Stopping the solution '$INTRINSIC_SOLUTION' started in the first steps."
(INTRINSIC_SOLUTION="" inctl solution stop "$INTRINSIC_SOLUTION" --org "$INTRINSIC_ORGANIZATION" --cluster "$lease_output")

echo "Waiting for solution to enter a not running state."

timeout_seconds=300 # 5 minutes
check_interval_seconds=10 
elapsed_seconds=0

while true; do
    status_output=$(inctl solution get "$INTRINSIC_SOLUTION" --org "$INTRINSIC_ORGANIZATION")

    if echo "$status_output" | grep -q "not running"; then
        echo "Solution '$INTRINSIC_SOLUTION' is not running."
        break 
    fi

    # Check for timeout
    if [ "$elapsed_seconds" -ge "$timeout_seconds" ]; then
        echo "Error: Timed out after $timeout_seconds seconds."
        echo "Last status check output:"
        echo "$status_output"
        exit 1
    fi

    echo "Not stopped yet. Retrying in $check_interval_seconds seconds."
    sleep "$check_interval_seconds"
    elapsed_seconds=$((elapsed_seconds + check_interval_seconds))
done

echo ""

echo "11. Return your VM"

echo "Returning your VM requested in the first steps."

inctl vm return "$lease_output" --org "$INTRINSIC_ORGANIZATION"

echo "---------------------------"
echo "CI Journey finished"
echo "---------------------------"
