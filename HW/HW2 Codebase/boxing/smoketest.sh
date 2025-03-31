#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}


##########################################################
#
# Boxer Management
#
##########################################################

create_boxer() {
  name=$1
  weight=$2
  height=$3
  reach=$4
  age=$5

  echo "Adding boxer ($name) to the ring..."
  curl -s -X POST "$BASE_URL/create-boxer" -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"weight\":\"$weight\", \"height\":$height, \"reach\":\"$reach\", \"age\":$age}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Boxer added successfully."
  else
    echo "Failed to add Boxer."
    exit 1
  fi
}

delete_boxer_by_id() {
  boxer_id=$1

  echo "Deleting boxer by ID ($boxer_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-boxer/$boxer_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer deleted successfully by ID ($boxer_id)."
  else
    echo "Failed to delete boxer by ID ($boxer_id)."
    exit 1
  fi
}

get_boxer_by_id() {
  boxer_id=$1

  echo "Getting boxer by ID ($boxer_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-id/$boxer_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer retrieved successfully by ID ($boxer_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON (ID $boxer_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxer by ID ($boxer_id)."
    exit 1
  fi
}

get_boxer_by_name() {
  boxer_name=$1

  echo "Getting boxer by name ($boxer_name)..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-name/$boxer_name")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer retrieved successfully by name ($boxer_name)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON (name $boxer_name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxer by name ($boxer_name)."
    exit 1
  fi
}

##########################################################
#
# Ring Management
#
##########################################################

enter_boxer_into_ring() {
  # Sends a POST request to enter a boxer into the ring
  # Args:
  #   $1: The name of the boxer to enter
  # Output:
  #   Echoes success or failure message to the console
  
  boxer_name=$1

  echo "Entering boxer '$boxer_name' into the ring..."
  response=$(curl -s -X POST "$BASE_URL/enter-ring/$boxer_name")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer '$boxer_name' successfully entered the ring."
  else
    echo "Failed to enter boxer '$boxer_name' into the ring."
    exit 1
  fi
}

simulate_fight() {
  # Sends a POST request to simulate a fight between the two boxers in the ring
  # Output:
  #   Echoes fight result if successful, or failure message

  echo "Simulating a fight..."
  response=$(curl -s -X POST "$BASE_URL/fight")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Fight simulation successful."
    if [ "$ECHO_JSON" = true ]; then
      echo "Fight result:"
      echo "$response" | jq .
    fi
  else
    echo "Fight simulation failed."
    exit 1
  fi
}
############################################################
#
# Leaderboard
#
############################################################


get_leaderboard() {
  echo "Getting leaderboard..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxers JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get leaderboard."
    exit 1
  fi
}

# Initialize the database
sqlite3 db/playlist.db < sql/init_db.sql

# Health checks
check_health
check_db

# Create boxers
create_boxer "John" 160 78 15.0 20
create_boxer "Burt" 150 78 12.0 21
create_boxer "Helen" 130 78 15.2 22
create_boxer "Mark" 133 78 14.0 23
create_boxer "Led" 155 78 15.3 29

delete_boxer_by_id 1
get_boxer_by_id 2
get_boxer_by_name "Mark"

#RING STUFF ( NEED TO ADD)
#
#
#
#

get_leaderboard

echo "All tests passed successfully!"
