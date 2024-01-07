import unittest
from unittest.mock import patch, MagicMock
from server import *

class TestServer(unittest.TestCase):

    @patch('builtins.input', side_effect=['<message>', ('127.0.0.1', 12345)])
    def test_login_command_success(self, mock_input):
        message_received = ['LOGIN', '<existing_user>', '<password>']
        address = ('127.0.0.1', 12345)
        result = loginCommand(message_received, address)
        self.assertEqual(result, 0)

    @patch('builtins.input', side_effect=['<message>', ('127.0.0.1', 12345)])
    def test_login_command_empty_username_or_password(self, mock_input):
        message_received = ['LOGIN', '', '']
        address = ('127.0.0.1', 12345)
        result = loginCommand(message_received, address)
        self.assertEqual(result, 1)

    @patch('builtins.input', side_effect=['<message>', ('127.0.0.1', 12345)])
    def test_login_command_incorrect_password(self, mock_input):
        message_received = ['LOGIN', '<abdo>', '<notabdo>']
        address = ('127.0.0.1', 12345)
        result = loginCommand(message_received, address)
        self.assertEqual(result, 3)

    @patch('builtins.input', side_effect=['<message>', ('127.0.0.1', 12345)])
    def test_login_command_username_not_found(self, mock_input):
        message_received = ['LOGIN', '<notabdo>', '<notabdo>']
        address = ('127.0.0.1', 12345)
        result = loginCommand(message_received, address)
        self.assertEqual(result, 2)

class TestSignupCommand(unittest.TestCase):

    @unittest.skip("Working, skipped because it floods database with every run if new credentials are given")
    @patch('builtins.input', side_effect=['<message>', ('127.0.0.1', 12345)])
    def test_signup_command_success(self, mock_input):
        message_received = ['SIGNUP', '<new_user2>', '<password>']
        address = ('127.0.0.1', 12345)
        result = signupCommand(message_received, address)
        self.assertEqual(result, 0)

    @patch('builtins.input', side_effect=['<message>', ('127.0.0.1', 12345)])
    def test_signup_command_username_taken(self, mock_input):
        message_received = ['SIGNUP', '<existing_user>', '<password>']
        address = ('127.0.0.1', 12345)
        result = signupCommand(message_received, address)
        self.assertEqual(result, 1)

    @patch('builtins.input', side_effect=['<message>', ('127.0.0.1', 12345)])
    def test_signup_command_failed(self, mock_input):
        # Mocking the database connection to simulate a failure
        with patch('server.sqlite3.connect', side_effect=Exception("Connection failed")):
            message_received = ['SIGNUP', '<new_user>', '<password>']
            address = ('127.0.0.1', 12345)
            result = signupCommand(message_received, address)
            self.assertEqual(result, 2)

class TestLogoutCommand(unittest.TestCase):

    @patch('builtins.input', side_effect=['<message>', ('127.0.0.1', 12345)])
    def test_logout_command_success(self, mock_input):
        # Assuming 'peersConnected' is a global variable in your module
        global peersConnected
        user_object = User(username='<username>', password='<password>', ip_address='127.0.0.1', port_number=12345, accept_peer_port_number=-1)
        peersConnected.append(user_object)

        result = logoutCommand(user_object)
        self.assertEqual(result, 0)

    @patch('builtins.input', side_effect=['<message>', ('127.0.0.1', 12345)])
    def test_logout_command_failed(self, mock_input):
        # Assuming 'peersConnected' is a global variable in your module
        global peersConnected
        user_object = User(username='<non_existing_user>', password='<password>', ip_address='127.0.0.1', port_number=12345, accept_peer_port_number=-1)

        result = logoutCommand(user_object)
        self.assertEqual(result, 1)

@unittest.skip("Needs adjusting")
class TestListOnlineUsersCommand(unittest.TestCase):

    @patch('server.socket.socket')
    def test_list_online_users_command_success(self, mock_socket):
        global peersConnected
        peersConnected = [
            MagicMock(username='user1', ip_address='127.0.0.1', port_number=12345),
            MagicMock(username='user2', ip_address='127.0.0.2', port_number=54321),
        ]

        mock_client = mock_socket.return_value
        mock_send_method = mock_client.send
        mock_send_method.return_value = None

        listOnlineUsersCommand(mock_client)

        expected_message = "ACCEPT 200 <user1 user2>"
        mock_send_method.assert_called_once_with(expected_message.encode('utf-8'))

    @patch('server.socket.socket')
    def test_list_online_users_command_failed(self, mock_socket):
        global peersConnected
        peersConnected = []

        mock_client = mock_socket.return_value
        mock_send_method = mock_client.send
        mock_send_method.return_value = None

        listOnlineUsersCommand(mock_client)

        mock_send_method.assert_called_once_with('FAILED 500'.encode('utf-8'))

class TestResetPasswordCommand(unittest.TestCase):

    @patch('builtins.input', side_effect=['<message>', ('127.0.0.1', 12345)])
    def test_reset_password_command_success(self, mock_input):
        message_received = ['RESET_PASSWORD', '<username>', '<new_password>']
        address = ('127.0.0.1', 12345)
        user_object = MagicMock(username='existing_user', ip_address='127.0.0.1', password='old_password', port_number=12345)
        peersConnected.append(user_object)

        result = resetPasswordCommand(message_received, address, user_object)
        self.assertEqual(result, 0)

    @patch('builtins.input', side_effect=['<message>', ('127.0.0.1', 12345)])
    def test_reset_password_command_failure(self, mock_input):
        message_received = ['RESET_PASSWORD', '<user>', '']
        address = ('127.0.0.1', 12345)
        user_object = MagicMock(username='existing_user', ip_address='127.0.0.1', password='old_password', port_number=12345)
        peersConnected.append(user_object)

        result = resetPasswordCommand(message_received, address, user_object)
        self.assertEqual(result, 1)

class TestCreateChatroomCommand(unittest.TestCase):

    @patch('builtins.input', side_effect=['<message>', '<chatroom_name>', '<new_port_number>'])
    def test_create_chatroom_command_success(self, mock_input):
        message_received = ['CREATE_CHATROOM', '<chatroom_name>', '<new_port_number>']
        user_object = MagicMock(username='existing_user', ip_address='127.0.0.1', password='password', port_number=12345)
        result = createChatroomCommand(message_received, user_object)

        self.assertEqual(result, 0)

    @patch('builtins.input', side_effect=['<message>', '<existing_chatroom>', '<new_port_number>'])
    def test_create_chatroom_command_name_exists(self, mock_input):
        message_received = ['CREATE_CHATROOM', '<existing_chatroom>', '<new_port_number>']
        user_object = MagicMock(username='existing_user', ip_address='127.0.0.1', password='password', port_number=12345)
        existing_chatroom = MagicMock(chatRoomName='existing_chatroom')
        chatroomsOnline.append(existing_chatroom)

        result = createChatroomCommand(message_received, user_object)

        self.assertEqual(result, 1)

    @patch('builtins.input', side_effect=['<message>', '<chatroom_name>', '<new_port_number>'])
    def test_create_chatroom_command_failure(self, mock_input):
        message_received = ['CREATE_CHATROOM', '<chatroom_name>', '<new_port_number>']
        user_object = MagicMock(username='existing_user', ip_address='127.0.0.1', password='password', port_number=12345)

        # Simulate an exception in the function
        with patch('server.ChatRoom', side_effect=Exception('Test exception')):
            result = createChatroomCommand(message_received, user_object)

        self.assertEqual(result, 2)

class TestDeleteChatroomCommand(unittest.TestCase):

    @unittest.skip("Needs adjusting")
    @patch('builtins.input', side_effect=['<message>', '<chatroom_name>'])
    def test_delete_chatroom_command_success(self, mock_input):
        message_received = ['DELETE_CHATROOM', '<chatroom_name>']
        result = deleteChatroomCommand(message_received)
        self.assertEqual(result, 0)

    @patch('builtins.input', side_effect=['<message>', '<nonexistent_chatroom>'])
    def test_delete_chatroom_command_failed(self, mock_input):
        message_received = ['DELETE_CHATROOM', '<nonexistent_chatroom>']
        result = deleteChatroomCommand(message_received)
        self.assertEqual(result, 1)

    @patch('builtins.input', side_effect=['<message>', '<invalid_input>', '<chatroom_name>'])
    def test_delete_chatroom_command_exception(self, mock_input):
        message_received = ['DELETE_CHATROOM', '<invalid_input>', '<chatroom_name>']
        result = deleteChatroomCommand(message_received)
        self.assertEqual(result, 1)

class TestJoinChatroomCommand(unittest.TestCase):
    
    @unittest.skip("Needs adjusting")
    @patch('builtins.input', side_effect=['<message>', '<existing_chatroom>'])
    def test_join_chatroom_command_success(self, mock_input):
        message_received = ['JOIN_CHATROOM', '<existing_chatroom>']

        result, ip_admin, port_admin = joinChatroomCommand(message_received)

        self.assertEqual(result, 0)
        self.assertNotEqual(ip_admin, 0)
        self.assertNotEqual(port_admin, 0)

    @patch('builtins.input', side_effect=['<message>', '<nonexistent_chatroom>'])
    def test_join_chatroom_command_failure(self, mock_input):
        message_received = ['JOIN_CHATROOM', '<nonexistent_chatroom>']

        result, ip_admin, port_admin = joinChatroomCommand(message_received)

        self.assertEqual(result, 1)
        self.assertEqual(ip_admin, 0)
        self.assertEqual(port_admin, 0)


if __name__ == '__main__':
    unittest.main()
