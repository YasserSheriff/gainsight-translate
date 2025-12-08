# Translate Service Application

This application exposes APIs to verify non-English text and translate the text to English.

This README will guide you through the steps to deploy the project locally, on OpenShift or IBM Code Engine. Additionally, you will learn how to access the Swagger documentation once the project is deployed.


## Deploying the application

### Deploying locally

To run application on your local machine, follow these steps:

1. Navigate to the project directory:

    ```bash
    cd gainsight-translate/application
    ```

3. Create a Python Enviroment, Activate it, and Install Requirements:

    ```bash
    python -m venv assetEnv
    source assetEnv/bin/activate
    pip install -r requirements.txt
    ```

5. Update your secrets:

    Copy `env` to `.env` and fill in the variables with your url, passwords, and apikeys.

    See the `env` file for more details on how to find the required values.

    | Name                   | Value                                                                                                 |
    | -----------------------| ----------------------------------------------------------------------------------------------------- |
    | APP_API_KEY        | Password used in the API header                                                                       |
    | ---------------------- | ----------------------------------------------------------------------------------------------------- |
    | IBM_CLOUD_API_KEY      | IBM Cloud API Key                                                                                     |
    | ---------------------- | ----------------------------------------------------------------------------------------------------- |
    | WX_LANGCHECK_URL       | watsonx language check deployemnt URL                                                                 |
    | ---------------------- | ----------------------------------------------------------------------------------------------------- |
    | WX_TRANSLATE_URL       | watsonx translate deployment URL                                                                      |
    | ---------------------- | ----------------------------------------------------------------------------------------------------- |

6. Start the project:

    ```bash
    python app.py
    ```

7. URL access:

    The url, for purposes of using cURL is http://0.0.0.0:4050.

    To access Swagger go to http://0.0.0.0:4050/docs


## Using the application APIs

After deploying the application, you can now test the API

### Test from Swagger

Open Swagger by going to `<url>/docs`.

#### langcheck

1. Authenticate the `langcheck` api by clicking the lock button to the right.  Enter the value you added for the `APP_API_KEY`.

2. Click the `Try it out` button and customize your request body:
    ```
    {
      "text": "je ne sais pas"
    }
    ```
3. Sample Response
    
    ```
    {
      "response": {"Requires_Translation": "true"}
    }
    ```

#### translate

1. Authenticate the `translate` api by clicking the lock button to the right.  Enter the value you added for the `APP_API_KEY`.

2. Click the `Try it out` button and customize your request body:
    
    ```
    {
      "text": "je ne sais pas"
    }
    ```

3. Response
    
    ```
    {
      "response": 
      {
        "Translation": "I don't know".
        "Language": "French"
      }
    }
    ```

