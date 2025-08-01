# !/bin/bash

echo "---This bash will go through all the CI journey ---"

# Variables setup

INTRINSIC_ORGANIZATION=""
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

echo "2. Deploy an existing solution."

echo "NOTE: You should have your solution running with the corresponding id."

echo "2.1. Checking the solution id."

if [ -z "$INTRINSIC_SOLUTION" ]; then
    inctl solution list --filter running_in_sim,running_on_hw --org "$INTRINSIC_ORGANIZATION"
    echo ""
    read -p "Please, copy the solution id: " INTRINSIC_SOLUTION
    if [ -z "$INTRINSIC_SOLUTION" ]; then
        echo "Error! Solution id wasn't set."
        exit 1
    else
        export INTRINSIC_SOLUTION="$INTRINSIC_SOLUTION"
        echo "Done! The INTRINSIC_SOLUTION has been set to: $INTRINSIC_SOLUTION"
    fi
else
    export INTRINSIC_SOLUTION="$INTRINSIC_SOLUTION"
    echo "Done! The INTRINSIC_SOLUTION has been set to: $INTRINSIC_SOLUTION"
fi

echo ""

echo "2.2. Get the solution from the id."

inctl solution get $INTRINSIC_SOLUTION --org "$INTRINSIC_ORGANIZATION"

echo ""

echo "3. Build the skill(s)."
echo "NOTE: You should have a skill created in order to build it in this step."

if [ -z "$SKILL_BAZEL" ]; then
    read -p "Please, write the skill bazel target name(s) (e.g my_skill): " SKILL_BAZEL < /dev/tty
    if [ -z "$SKILL_BAZEL" ]; then
        echo "Error! Bazel skill target name(s) was not set."
    fi
fi

IFS=',' read -ra SKILL_ARRAY <<< "$SKILL_BAZEL"

for SKILL in "${SKILL_ARRAY[@]}"; do
    SKILL=$(echo "$SKILL" | xargs)
    if [ -n "$SKILL" ]; then
        echo "Building the skill with the target $SKILL"
        bazel build //"$SKILL"
        if [ $? -ne 0 ]; then
            echo "Error: Bazel build for skill '$SKILL' failed. Exiting."
            exit 1
        fi
    fi
done

echo ""

echo "4. Install the skill(s)."

INSTALLED_SKILLS=$(inctl skill list --org "$INTRINSIC_ORGANIZATION" --solution "$INTRINSIC_SOLUTION")

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
            inctl skill uninstall --type=id "com.example.${skill_name}" --org "$INTRINSIC_ORGANIZATION" --solution "$INTRINSIC_SOLUTION"
        fi
        echo "Installing skill: $SKILL"
        inctl skill install bazel-bin/"$skill_package"/"$skill_target".bundle.tar --solution "$INTRINSIC_SOLUTION" --org "$INTRINSIC_ORGANIZATION"
        if [ $? -ne 0 ]; then
            echo "Error: Skill installation for '$SKILL' failed. Exiting."
        fi
    fi
done

echo ""

echo "5. Build the service(s)"
echo "NOTE: You should have a service created in order to build it in this step."

if [ -z "$SERVICE_BAZEL" ]; then
    read -p "Please, write the service bazel target name(s) (e.g my_service): " SERVICE_BAZEL < /dev/tty
    if [ -z "$SERVICE_BAZEL" ]; then
        echo "Error! Bazel service target name(s) was not set."
    fi
fi

IFS=',' read -ra SERVICE_ARRAY <<< "$SERVICE_BAZEL"

for SERVICE in "${SERVICE_ARRAY[@]}"; do
    SERVICE=$(echo "$SERVICE" | xargs)
    if [ -n "$SERVICE" ]; then
        echo "Building the service with the target $SERVICE"
        bazel build //"$SERVICE"
        if [ $? -ne 0 ]; then
            echo "Error: Bazel build for service '$SERVICE' failed. Exiting."
            exit 1
        fi
    fi
done

echo ""

echo "6. Install the service(s)."

INSTALLED_SERVICES=$(inctl service list --org "$INTRINSIC_ORGANIZATION" --solution "$INTRINSIC_SOLUTION")

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
            inctl service uninstall "com.example.${service_target}" --org "$INTRINSIC_ORGANIZATION" --solution "$INTRINSIC_SOLUTION"
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

echo "7. Add the service(s)."

echo "7.1 Listing your installed assets for services"

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
done < <(inctl service list --org "$INTRINSIC_ORGANIZATION" --solution "$INTRINSIC_SOLUTION")

echo "7.2 Add the service(s)"

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
echo "8. Add a process that uses the skill and service."

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

echo "---------------------------"
echo "CI Journey finished"
echo "---------------------------"
