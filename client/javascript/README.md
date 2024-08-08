# Conducteur javascript Client

A simple client for the Javascript conducteur API.

## Quickstart
` npm install conducteur `

in a file:
```javascript
import {Conducteur} from 'conducteur';
const apiUrl = 'https://api.example.com'
const token = 'your-token-here'

const conducteur = new Conducteur(apiUrl, token);

// Setup your prediction params
const dockerImage = 'yassinsiouda/cog-html';
const input = {
    "url": "https://google.fr"
}

const result = await conducteur.predict(dockerImage, input)

console.log(result);

```

