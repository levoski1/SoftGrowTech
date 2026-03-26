# Expense Tracker

A comprehensive Python-based expense tracking application with analytics, data validation, and export capabilities.

## Features

- **Expense Management**: Create, read, update, and delete expense entries
- **Analytics**: Track spending patterns and generate detailed reports
- **Data Validation**: Ensure data integrity with comprehensive validators
- **Export**: Export expense data to various formats
- **Display**: User-friendly interface for viewing expenses
- **Seed Data**: Sample data for testing and demonstration

## Project Structure

```
Task1/Expense_Tracker/
├── main.py                 # Main application entry point
├── expense_tracker.py      # Core expense tracking functionality
├── analytics.py            # Analytics and reporting
├── display.py              # Display and UI components
├── export.py               # Export functionality
├── validators.py           # Data validation functions
├── seed_data.py            # Sample data generation
├── data/
│   └── expenses.json       # Expense data storage
├── README.md               # Detailed documentation
└── DOCUMENTATION.md        # Technical documentation
```

## Requirements

- Python 3.12+
- Virtual environment (included in `env/`)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd SoftGrowTech
```

2. Create and activate virtual environment:
```bash
python3 -m venv env
source env/bin/activate
```

3. Install dependencies (if required):
```bash
pip install -r requirements.txt
```

## Usage

Run the main application:
```bash
python Task1/Expense_Tracker/main.py
```

### Key Commands

- **Track Expense**: Add a new expense entry
- **View Analytics**: Generate spending reports
- **Export Data**: Export expenses to file
- **View All Expenses**: Display expense list

## Configuration

See `DOCUMENTATION.md` for detailed configuration and API documentation.

## Development

To seed sample data:
```bash
python Task1/Expense_Tracker/seed_data.py
```

## File Descriptions

- **main.py**: Application entry point and main loop
- **expense_tracker.py**: Core expense management logic
- **analytics.py**: Spending analysis and reporting
- **display.py**: Console interface and formatting
- **export.py**: Data export to different formats
- **validators.py**: Input validation and error handling
- **seed_data.py**: Generate test data

## License

[Your License Here]

## Contributing

1. Create a feature branch
2. Make your changes
3. Submit a pull request

