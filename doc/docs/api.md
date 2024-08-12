# HTTP API Reference

## Predictions

Prediction represent an inference job waiting to be processed.or already processed with a result

Create/Delete/List Predictions

<details>
 <summary><code>POST</code> <code><b>/predict</b></code> <code>Create a new prediction</code></summary>

##### Parameters

| Name  | type     | data type | description                                      |
| ----- | -------- | --------- | ------------------------------------------------ |
| image | required | string    | The name of the cog docker image you want to use |
| input | required | object    | the input object for your cog image              |
|       |          |           |                                                  |

##### Responses

| http code | content-type               | response                                                                  |
| --------- | -------------------------- | ------------------------------------------------------------------------- |
| 200       | `application/json`         | Prediction Object                                                         |
| 403       | `text/plain;charset=UTF-8` | Not Authorized                                                            |
| 403       | `text/plain;charset=UTF-8` | The image is not within the scope of your token.                          |
| 503       | `text/plain;charset=UTF-8` | No available nodes                                                        |
| 500       | `text/plain;charset=UTF-8` | Cog setup failed with error {error message}                               |
| 403       | `text/plain;charset=UTF-8` | The health_check timed out check your container logs for more information |
| 403       | `text/plain;charset=UTF-8` | Timeout: Container {container.id} did not start within {timeout} seconds  |
| 404       | `text/plain;charset=UTF-8` | The Docker image you are trying to run does not exist.                    |
| 403       | `text/plain;charset=UTF-8` | Could not run the Docker image due to {error message}                     |


**Prediction Object**
```json
{
    "input": {
        "image": "string"
    },
    "output": "string",
    "id": null,
    "version": null,
    "created_at": null,
    "started_at": "string",
    "completed_at": "string",
    "logs": "",
    "error": null,
    "status": "string",
    "metrics": {
        "predict_time": number
    },
    "webhook": null,
    "webhook_events_filter": ["start", "output", "logs", "completed"],
    "output_file_prefix": null,
    "co2": number
}
```


**Example curl** 