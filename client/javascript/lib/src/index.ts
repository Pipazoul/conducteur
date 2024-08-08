export class Conducteur {
  public baseUrl: string;
  public token: string;

  constructor(baseUrl: string , token: string) {
      this.baseUrl = baseUrl
      this.token = token
  }
  async predict(image: string, input: object) {
      const response = await fetch(`${this.baseUrl}/predict`, {
    method: 'POST',
    headers: {
             'Content-Type': 'application/json',
             'Authorization': `Bearer ${this.token}`
          },
    body: JSON.stringify({
      image: image,
      input: input
    })
  });
      const data = await response.json();
      return data
  }
}


module.exports = {
  Conducteur
};