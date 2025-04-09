#!/usr/bin/env bash
# Simple visualization script for People Analytics
# This makes it even easier to generate visualizations

# Set default values
DATA_PATH="./test_data"
OUTPUT_DIR="./output"
YEAR=""
PERSON=""
TYPE="interactive"
TITLE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --data-path)
      DATA_PATH="$2"
      shift 2
      ;;
    --output-directory)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --year)
      YEAR="$2"
      shift 2
      ;;
    --person)
      PERSON="$2"
      shift 2
      ;;
    --type)
      TYPE="$2"
      shift 2
      ;;
    --title)
      TITLE="$2"
      shift 2
      ;;
    --help|-h)
      echo "Usage: visualize.sh [options]"
      echo "Options:"
      echo "  --data-path PATH   Path to evaluation data (default: ./test_data)"
      echo "  --output-directory DIR   Directory to save output (default: ./output)"
      echo "  --year YEAR        Year to visualize"
      echo "  --person PERSON    Person to visualize (for radar charts)"
      echo "  --type TYPE        Type of visualization (radar, heatmap, interactive)"
      echo "  --title TITLE      Title for the visualization"
      echo "  --help, -h         Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

# Set default title if not provided
if [ -z "$TITLE" ]; then
  if [ -n "$PERSON" ] && [ -n "$YEAR" ]; then
    TITLE="Performance Report - $PERSON ($YEAR)"
  elif [ -n "$YEAR" ]; then
    TITLE="Performance Report - $YEAR"
  else
    TITLE="Performance Report"
  fi
fi

# Determine output file
if [ "$TYPE" == "radar" ]; then
  OUTPUT_FILE="$OUTPUT_DIR/radar_${PERSON:-all}_${YEAR:-all}.png"
elif [ "$TYPE" == "heatmap" ]; then
  OUTPUT_FILE="$OUTPUT_DIR/heatmap_${YEAR:-all}.png"
elif [ "$TYPE" == "interactive" ]; then
  OUTPUT_FILE="$OUTPUT_DIR/report_${YEAR:-all}.html"
else
  echo "Error: Unknown visualization type: $TYPE"
  exit 1
fi

# Build and run the command
CMD="python -m peopleanalytics --base-path $DATA_PATH visualize --type $TYPE --output $OUTPUT_FILE --title \"$TITLE\""

if [ -n "$YEAR" ]; then
  CMD="$CMD --year $YEAR"
fi

if [ -n "$PERSON" ]; then
  CMD="$CMD --person $PERSON"
fi

echo "Running: $CMD"
eval "$CMD"

echo "Visualization saved to: $OUTPUT_FILE" 