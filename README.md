# Gmail Smart Inbox

A powerful tool for analyzing and organizing your Gmail inbox using intelligent automation and insights.

## 🌟 Features

- Smart email categorization and analysis
- Inbox insights and statistics
- Automated email organization
- Custom filtering and processing rules

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- Gmail account with API access
- Google Cloud Project with Gmail API enabled

### Installation

1. Clone the repository:
```bash
git clone https://github.com/aagrawal52/gmail-smart-inbox.git
cd gmail-smart-inbox
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your Google Cloud credentials:
   - Create a project in Google Cloud Console
   - Enable Gmail API
   - Download credentials and save as `credentials.json` in the project root
   - Run the application once to generate `token.json`

## 📝 Usage

Run the main application:
```bash
python inbox_insights/main.py
```

## 📁 Project Structure

```
gmail-smart-inbox/
├── inbox_insights/
│   ├── config/       # Configuration files
│   ├── data/        # Data storage and processing
│   ├── src/         # Source code
│   ├── utils/       # Utility functions
│   └── main.py      # Main application entry point
├── requirements.txt  # Python dependencies
└── README.md        # Project documentation
```

## 🔒 Security

- This application uses OAuth 2.0 for authentication
- Credentials are stored locally and securely
- No email data is stored permanently unless explicitly configured

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For any questions or feedback, please open an issue in the GitHub repository.

## 🙏 Acknowledgments

- Google Gmail API
- Python Gmail libraries and tools
- Contributors and maintainers