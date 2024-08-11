// Create enum status with values 'offline', 'ongoing', and 'completed'.
export enum Status {
    unknown = "unknown",
    available = "available",
    offline = "offline",
    busy = "busy"
}

export interface User {
  name: string,
  token: string,
  scope?: Array<string>,
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
  co2: string | null;
}


export interface Predictions {
  total_co2: number;
  total_duration: number;
  predictions: Array<PredictionResponse>;
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
    try {
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
      switch (data.status) {
        case 'available': return Status.available;
        case 'offline': return Status.offline;
        default: throw  Status.unknown;
      }
    }
    catch(e) {
      console.error('Error in status', e);
      return Status.offline;
    }
  }
  async user(): Promise<User>  {
    const response = await fetch(`${this.baseUrl}/user`, {
      method: 'POST',
      headers:  {
                'Content-Type':  'application/json',
                'Authorization': `Bearer ${this.token}`
              },
              });
    const data = await response.json();
    return data;
   }

  async predictions(start?:string, end?: string): Promise<Predictions> {
    // if start or and is provider verify format DD-MM-YYYY and throw error if not valid
    const dateRegex = /^\d{2}-\d{2}-\d{4}$/;
    const user = (await this.user()).name
    let payload  = {};
    if (start && end){
      console.log("start and end", start, end)
      if (!dateRegex.test(start) || !dateRegex.test(end)) {
        throw new Error('Invalid date format');
      }
      payload = {
        start,
        end,
        user
      }
    }
    else {
      payload = {user};
    }
    
    const response = await fetch(`${this.baseUrl}/user/predictions/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`
      },
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    return data;
  }

}


module.exports = {
  Conducteur
};
