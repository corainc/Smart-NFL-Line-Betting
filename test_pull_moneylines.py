import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
import pull_moneylines as pnl

class TestPullMoneylines(unittest.TestCase):

    @patch('pull_moneylines.requests.get')
    def test_fetch_webpage_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'<html></html>'
        
        content = pnl.fetch_webpage('https://www.test.com')
        self.assertIsNotNone(content)
        self.assertEqual(content, b'<html></html>')

    @patch('pull_moneylines.BeautifulSoup')
    def test_parse_html(self, mock_soup):
        content = '<html><body></body></html>'
        soup = pnl.parse_html(content)
        mock_soup.assert_called_with(content, 'html.parser')

    def test_format_dataframe(self):
        data = [
            {'date': '2023-10-05', 'time': '10:00 AM',
             'game': 0, 'team': 'DEN', 'flag': 'Away Team', 'ml': '-110'},
            {'date': '2023-10-05', 'time': '10:00 AM',
             'game': 0, 'team': 'NYJ', 'flag': 'Home Team', 'ml': '-110'}
        ]
        df = pnl.format_dataframe(data)
        self.assertEqual(df.shape[0], len(data))

if __name__ == '__main__':
    unittest.main()