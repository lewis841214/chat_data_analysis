# Chat Data Analysis

A comprehensive framework for analyzing conversation data from various messaging platforms.

## Architecture

The framework consists of the following components:

1. **Platform Handlers** - Process platform-specific data (Facebook, etc.) and convert to a standardized format
2. **Feature Processors** - Extract features and targets from standardized conversation data
3. **Visualization** - Generate plots and visualizations of features and targets

### Flow Diagram

```
Raw Platform Data -> Platform Handlers -> Standardized Data -> Feature Processors -> Features/Targets -> Visualization
```

### Directory Structure

```
chat_data_analysis/
├── configs/
│   └── facebook_analysis_config.yaml
├── platform_handlers/
│   ├── base_handler.py
│   ├── facebook_handler.py
│   ├── generic_handler.py
│   └── handler_factory.py
├── feature_processor/
│   ├── base_processor.py
│   ├── processor_factory.py
│   ├── features/
│   │   ├── message_count.py
│   │   ├── message_length.py
│   │   └── response_time.py
│   └── targets/
│       ├── response_rate.py
│       ├── user_engagement.py
│       └── conversation_duration.py
└── visualization/
    ├── visualizer.py
    └── plotter.py
```

## Usage

To run the analysis pipeline:

```bash
source /home/lewis/1project/Chat_data_preprocessing/venv/bin/activate
python pipeline.py --config configs/default_config.yaml
```

## Adding New Components

### Adding a New Feature Extractor

1. Create a new file in `feature_processor/features/` (e.g., `emoji_usage.py`)
2. Define a class that inherits from `BaseFeatureExtractor`
3. Implement the `extract()` method
4. The feature will be automatically discovered and loaded

Example:

```python
from feature_processor.base_processor import BaseFeatureExtractor

class EmojiUsageExtractor(BaseFeatureExtractor):
    def extract(self, conversation):
        # Extract and return emoji usage features
        return {"emoji_count": 42}
```

### Adding a New Target Extractor

1. Create a new file in `feature_processor/targets/` (e.g., `sentiment_score.py`)
2. Define a class that inherits from `BaseTargetExtractor`
3. Implement the `extract()` method
4. The target will be automatically discovered and loaded

Example:

```python
from feature_processor.base_processor import BaseTargetExtractor

class SentimentScoreExtractor(BaseTargetExtractor):
    def extract(self, conversation):
        # Calculate and return sentiment score
        return 0.75  # Positive sentiment
```

### Adding a New Platform Handler

1. Create a new file in `platform_handlers/` (e.g., `discord_handler.py`)
2. Define a class that inherits from `BasePlatformHandler`
3. Implement the `transform()` method to convert platform data to standardized format
4. Register the handler in `handler_factory.py`

## Standardized Data Format

All platform handlers convert data to this standardized format:

```json
{
  "conversation_id": "unique_id",
  "platform": "facebook",
  "created_at": "2023-01-01T12:00:00",
  "participants": ["User", "Assistant"],
  "conversation": [
    {
      "sender_name": "User",
      "timestamp_ms": 1672567200000,
      "content": "Hello, how can I help you?"
    },
    {
      "sender_name": "Assistant",
      "timestamp_ms": 1672567230000,
      "content": "I have a question about..."
    }
  ]
}
```

## Configuration

The configuration file controls all aspects of the pipeline:

- **Platform Handlers**: Which platform to process and its settings
- **Feature Processors**: Which features and targets to extract
- **Visualization**: How to visualize the features and targets

See `configs/facebook_analysis_config.yaml` for an example configuration.

## Output

The pipeline generates several outputs:

1. Standardized conversation data
2. Extracted features and targets
3. Visualizations of features and targets 