## .env File Example

```
GEMINI_API_KEY=_apikeyhere_
INSTRUCTIONS=_custom instruction for your ai_
```

## How to Run on Linux

1. Navigate to the project directory:
    ```sh
    cd IsAIti
    ```

2. Create and activate a virtual environment:
    ```sh
    python3 -m venv venv
    source venv/bin/activateˆ
    ```

3. Install the required dependencies:
    ```sh
    pip install fastapi uvicorn pydantic python-dotenv google-genai
    ```

4. Start the server:
    ```sh
    uvicorn main:app 
    ```
    - Server now will ask you to put a tcp server ip and port
    - Ensure the server is set to `0.0.0.0` to accept all incoming connections.
    - Add port number between 10000 and 14000.
    - Disable the firewall if needed.

## Running the Human Client

- **On another device:**
    - Ensure both devices are on the same network.
    - Provide the server IP and the port used as arguments.

- **On the same device:**
    - Use `localhost` and the port used as arguments.

## Playing with Python Player

Once everything is set up, you can use `python_player` to play, or use the Web Front-End (TBD).