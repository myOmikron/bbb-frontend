# BBB Frontend

This project serves as frontend for the user.

## API

### Authentication
Authentication to the API is done via [RCP](https://github.com/myOmikron/rcp).
The endpoint is used as salt whereas the key for the checksum is `checksum`.
The authentication is required at every endpoint.

### `/api/v1/join`

This method is used to validate a users request and if successful, forward to `watch`.

- Method: `GET`

Parameter  | Required | Description
:---:      | :---:    | :---:
user_name  | Yes      | The name of the user that should be displayed
meeting_id | Yes      | The meeting_id of a bbb meeting

### `/api/v1/openChannel`

This method is used to open a new channel. It returns a streaming key which grants access to the rtmp server.
The data has to be a valid json object.

- Method `POST`

Parameter   | Required | Description
:---:       | :---:    | :---:
meeting_id  | Yes      | The meeting_id of a bbb meeting
welcome_msg | No       | The message that should be displayed above the chat. HTML is allowed.

Returns a json on success:
```json
{
  "success": true,
  "message": "New Channel was created",
  "content": {
    "streaming_key": "streaming_key"
  }
}
```

### `/api/v1/closeChannel`

This method is used to close an open channel. The data has to be a valid json object.

- Method `POST`

Parameter  | Description
:---:      | :---:
meeting_id | The meeting_id of a bbb meeting

Returns a json on success:
```json
{
  "success": true,
  "message": "Channel was deleted"
}
```