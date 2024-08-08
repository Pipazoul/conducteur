// Create enum status with values 'offline', 'ongoing', and 'completed'.
export enum Status {
    unknown = "unknown",
    available = "available",
    offline = "offline",
    busy = "busy"
}

export interface PredictionResponse {
  output: string;
  id: string | null;
  version: string | null;
  created_at: Date | null;
  started_at: Date | null;
  completed_at: Date | null;
  logs: string ;
  error: object | null;
  status: string; 
  metrics: { predict_time: number };
  output_file_prefix: string | null;
  webhook_events_filter: Array<string>;
  webhook: string | null;
}


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

  async status(): Promise<Status> {
    const response = await fetch(`${this.baseUrl}/status`, {
      method: 'GET',
      headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${this.token}`
            },
    });
    // check if response is ok
    if (!response.ok) {
      return Status.offline;
    }
    const data = await response.json();
    // for each item in the array, if on item state is available set it to online if all items are busy then return busy else return offline
    let status = Status.unknown;
    let allBusy = true;
    for (let item of data) {
      if (item.state == "available") {
        status = Status.available;
        allBusy  = false;
        break;
      } else if (item.state == "busy") {
        continue;
      } else {
        status = Status.offline;
      }
    }
    if (allBusy)  {
      status = Status.busy;
    }
    return status;
  }
}


module.exports = {
  Conducteur
};


let baseUrl = 'https://conducteur.distributed.homes';
let token = "trckbJz828tztR2PWALD9dAqVRuCd"
let conducteur = new Conducteur(baseUrl, token);

console.log("Status: ", conducteur.status().then((res) => console.log(res)));
