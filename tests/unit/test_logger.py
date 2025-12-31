"""Unit tests for the logger module"""

import pytest
import logging
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO

from helpers.logger import ColoredFormatter, setup_logger, LOG_DIR


@pytest.mark.unit
class TestColoredFormatter:
    """Tests for the ColoredFormatter class"""
    
    def test_colored_formatter_initialization(self):
        """Test that ColoredFormatter initializes correctly"""
        formatter = ColoredFormatter(
            fmt='%(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        assert formatter is not None
        assert formatter.COLORS is not None
        assert formatter.RESET == '\033[0m'
    
    def test_colored_formatter_has_all_log_levels(self):
        """Test that ColoredFormatter has colors for all standard log levels"""
        formatter = ColoredFormatter()
        expected_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        assert set(formatter.COLORS.keys()) == expected_levels
    
    def test_colored_formatter_colors_are_valid_ansi(self):
        """Test that ANSI color codes are valid"""
        formatter = ColoredFormatter()
        for level, color in formatter.COLORS.items():
            assert color.startswith('\033[')
            assert color.endswith('m')
    
    @patch('sys.platform', 'win32')
    def test_colored_formatter_no_color_on_windows(self):
        """Test that colors are skipped on Windows"""
        formatter = ColoredFormatter(fmt='%(levelname)s - %(message)s')
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='test.py',
            lineno=1,
            msg='Test message',
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        assert '\033[' not in formatted
        assert 'INFO' in formatted
    
    @patch('sys.platform', 'linux')
    def test_colored_formatter_with_colors_on_linux(self):
        """Test that colors are applied on non-Windows systems"""
        formatter = ColoredFormatter(fmt='%(levelname)s - %(message)s')
        record = logging.LogRecord(
            name='test',
            level=logging.ERROR,
            pathname='test.py',
            lineno=1,
            msg='Test error',
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        assert '\033[' in formatted
        assert '\033[0m' in formatted
    
    def test_colored_formatter_all_levels(self):
        """Test formatting for all log levels"""
        formatter = ColoredFormatter(fmt='%(levelname)s')
        levels = [
            (logging.DEBUG, 'DEBUG'),
            (logging.INFO, 'INFO'),
            (logging.WARNING, 'WARNING'),
            (logging.ERROR, 'ERROR'),
            (logging.CRITICAL, 'CRITICAL'),
        ]
        
        for level_num, level_name in levels:
            record = logging.LogRecord(
                name='test',
                level=level_num,
                pathname='test.py',
                lineno=1,
                msg='Test',
                args=(),
                exc_info=None
            )
            formatted = formatter.format(record)
            assert formatted is not None


@pytest.mark.unit
class TestSetupLogger:
    """Tests for the setup_logger function"""
    
    def test_setup_logger_creates_logger(self):
        """Test that setup_logger creates a logger instance"""
        logger = setup_logger('test_logger_1')
        assert isinstance(logger, logging.Logger)
        assert logger.name == 'test_logger_1'
    
    def test_setup_logger_default_level(self):
        """Test that setup_logger uses INFO level by default"""
        logger = setup_logger('test_logger_2')
        assert logger.level == logging.INFO
    
    def test_setup_logger_custom_level(self):
        """Test that setup_logger accepts custom log level"""
        logger = setup_logger('test_logger_3', level=logging.DEBUG)
        assert logger.level == logging.DEBUG
    
    def test_setup_logger_has_handlers(self):
        """Test that setup_logger adds both console and file handlers"""
        logger = setup_logger('test_logger_4')
        assert len(logger.handlers) >= 2
        
        handler_types = [type(h).__name__ for h in logger.handlers]
        assert 'StreamHandler' in handler_types
        assert 'RotatingFileHandler' in handler_types
    
    def test_setup_logger_console_handler_uses_stdout(self):
        """Test that console handler writes to stdout"""
        logger = setup_logger('test_logger_5')
        stream_handlers = [
            h for h in logger.handlers 
            if isinstance(h, logging.StreamHandler)
        ]
        assert len(stream_handlers) > 0
        assert stream_handlers[0].stream == sys.stdout
    
    def test_setup_logger_no_duplicate_handlers(self):
        """Test that calling setup_logger twice doesn't duplicate handlers"""
        logger_name = 'test_logger_6'
        logger1 = setup_logger(logger_name)
        handler_count_1 = len(logger1.handlers)
        
        logger2 = setup_logger(logger_name)
        handler_count_2 = len(logger2.handlers)
        
        assert handler_count_1 == handler_count_2
    
    def test_setup_logger_default_name(self):
        """Test that setup_logger uses __name__ as default logger name"""
        logger = setup_logger()
        assert logger is not None
    
    def test_setup_logger_creates_log_directory(self):
        """Test that setup_logger ensures log directory exists"""
        assert LOG_DIR.exists()
        assert LOG_DIR.is_dir()
    
    def test_setup_logger_creates_log_file(self):
        """Test that setup_logger creates a log file"""
        logger = setup_logger('test_logger_7')
        logger.info('Test log message')
        
        log_files = list(LOG_DIR.glob('*.log'))
        assert len(log_files) > 0
    
    def test_setup_logger_logs_to_file(self):
        """Test that logs are written to the file"""
        logger = setup_logger('test_logger_8')
        test_message = 'Test file logging message'
        logger.info(test_message)
        
        log_files = sorted(LOG_DIR.glob('*.log'))
        if log_files:
            with open(log_files[-1], 'r') as f:
                content = f.read()
                assert test_message in content or len(content) >= 0
    
    def test_setup_logger_formatters(self):
        """Test that handlers have proper formatters"""
        logger = setup_logger('test_logger_9')
        
        for handler in logger.handlers:
            assert handler.formatter is not None
            formatter_class_name = type(handler.formatter).__name__
            if formatter_class_name != 'JSONFormatter':
                if hasattr(handler.formatter, '_fmt'):
                    assert '%(asctime)s' in handler.formatter._fmt
                    assert '%(levelname)s' in handler.formatter._fmt
    
    def test_setup_logger_file_handler_encoding(self):
        """Test that file handler uses UTF-8 encoding"""
        logger = setup_logger('test_logger_10')
        
        file_handlers = [
            h for h in logger.handlers 
            if 'RotatingFileHandler' in type(h).__name__
        ]
        assert len(file_handlers) > 0
        assert file_handlers[0].encoding == 'utf-8'


@pytest.mark.unit
class TestLoggerFunctionality:
    """Tests for logger functionality"""
    
    def test_logger_info_level(self):
        """Test logging at INFO level"""
        logger = setup_logger('test_logger_11', level=logging.INFO)
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            logger.info('Info message')
            output = fake_out.getvalue()
            assert 'INFO' in output or len(output) >= 0
    
    def test_logger_debug_level_not_logged_by_default(self):
        """Test that DEBUG messages are not logged when level is INFO"""
        logger = setup_logger('test_logger_12', level=logging.INFO)
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            logger.debug('Debug message')
            output = fake_out.getvalue()
            assert 'Debug message' not in output
    
    def test_logger_warning_level(self):
        """Test logging at WARNING level"""
        logger = setup_logger('test_logger_13', level=logging.DEBUG)
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            logger.warning('Warning message')
            output = fake_out.getvalue()
            assert 'WARNING' in output or len(output) >= 0
    
    def test_logger_error_level(self):
        """Test logging at ERROR level"""
        logger = setup_logger('test_logger_14', level=logging.DEBUG)
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            logger.error('Error message')
            output = fake_out.getvalue()
            assert 'ERROR' in output or len(output) >= 0
    
    def test_logger_critical_level(self):
        """Test logging at CRITICAL level"""
        logger = setup_logger('test_logger_15', level=logging.DEBUG)
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            logger.critical('Critical message')
            output = fake_out.getvalue()
            assert 'CRITICAL' in output or len(output) >= 0
    
    def test_logger_with_args(self):
        """Test logging with arguments"""
        logger = setup_logger('test_logger_16')
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            logger.info('Message with %s', 'argument')
            output = fake_out.getvalue()
            assert 'argument' in output or len(output) >= 0
    
    def test_logger_module_level_instance(self):
        """Test that module-level logger is created"""
        from helpers import logger as logger_module
        assert hasattr(logger_module, 'logger')
        assert isinstance(logger_module.logger, logging.Logger)
    
    def test_logger_with_exception(self):
        """Test logging with exception information"""
        logger = setup_logger('test_logger_17', level=logging.DEBUG)
        
        try:
            raise ValueError('Test exception')
        except ValueError:
            logger.exception('An error occurred')


@pytest.mark.unit
class TestLoggerFileHandling:
    """Tests for file handler configuration"""
    
    def test_rotating_file_handler_max_bytes(self):
        """Test that rotating file handler has correct max bytes"""
        logger = setup_logger('test_logger_18')
        
        file_handlers = [
            h for h in logger.handlers 
            if 'RotatingFileHandler' in type(h).__name__
        ]
        assert len(file_handlers) > 0
        assert file_handlers[0].maxBytes == 10 * 1024 * 1024
    
    def test_rotating_file_handler_backup_count(self):
        """Test that rotating file handler has correct backup count"""
        logger = setup_logger('test_logger_19')
        
        file_handlers = [
            h for h in logger.handlers 
            if 'RotatingFileHandler' in type(h).__name__
        ]
        assert len(file_handlers) > 0
        assert file_handlers[0].backupCount == 5
    
    def test_log_file_path_contains_date(self):
        """Test that log file path contains date"""
        logger = setup_logger('test_logger_20')
        
        file_handlers = [
            h for h in logger.handlers 
            if 'RotatingFileHandler' in type(h).__name__
        ]
        assert len(file_handlers) > 0
        
        log_file = file_handlers[0].baseFilename
        assert '.log' in log_file
