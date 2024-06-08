<script lang="ts">
    import { PUBLIC_ENV } from '$env/static/public'
    import { Area, Axis, Bars, Chart, Highlight, LinearGradient, RectClipPath, Svg, Tooltip, TooltipItem } from "layerchart";
    import { scaleBand } from "d3-scale";
    import { onMount } from "svelte";
  	import { page } from "$app/stores";
  
    interface Prediction {
      user: string;
      image: string;
      status: string;
      started: string; // YYYY-MM-DD HH:MM:SS
      finished: string; // YYYY-MM-DD HH:MM:SS
      duration: number;
    }
    let environment = PUBLIC_ENV || 'prod';
    let url = environment === 'prod' ? '/predictions/' : 'http://localhost:8000/predictions/';
    let predictions: Prediction[] = [];
    let filteredPredictions: Prediction[] = [];
    let filterDuration = '6h'; // Default filter
    let selectedUser: string | null = null;
    let currentPageUrl = '';
    let token = '';

    const timeFilters = {
        '5min': 0.08333333333333333,
        '15min': 0.25,
        '30min': 0.5,
        '1h': 1,
        '2h': 2,
        '4h': 4,
        '6h': 6,
        '12h': 12,
        '24h': 24,
    };
  
    onMount(async () => {
        token = localStorage.getItem('token') || '';
        await getPredictions();
        filteredPredictions = predictions;
        filter();
        // setInterval(getPredictions, 1000); // Uncomment for periodic updates
    });
    
    async function setToken(token: string) {
        localStorage.setItem('token', token);
        await getPredictions();
        filteredPredictions = predictions;
        token_modal.close();
    }
  
    async function getPredictions() {
    try {
        const headers = new Headers();
        headers.set("Authorization", `Bearer ${token}`);
        //const response = await fetch("http://localhost:8000/predictions", {
        const response = await fetch(url, {
            headers,
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        // Get the current time and subtract 24 hours
        const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);

        // Filter the predictions to only include those finished within the last 24 hours
        predictions = data.filter(prediction => {
            const finishedTime = new Date(prediction.finished);
            return finishedTime >= oneDayAgo;
        });
    } catch (error) {
        console.error(error);
    }
}
  
    async function filter() {
        const now = new Date();
        const durationHours = timeFilters[filterDuration]; // Corrected line

        const timeLimit = new Date(now.getTime() - durationHours * 3600 * 1000);

        let userFilteredPredictions = filterByUser();

        filteredPredictions = userFilteredPredictions.filter(prediction => {
            const finishedTime = new Date(prediction.finished);
            return finishedTime && finishedTime > timeLimit;
        });
    }

    function filterByUser() {
        if (selectedUser) {
            return predictions.filter(prediction => prediction.user === selectedUser);
        }
        return predictions;
    }


  </script>
  
  <section class="p-4">
    <div class="flex justify-end absolute right-4 top-4">
        <button class="btn" onclick="token_modal.showModal()">🔑</button>
    </div>
    <h1 class="text-2xl uppercase font-bold mb-4">🚊 Conducteur Stats</h1>
    <div class="flex space-x-4 pb-4">
        <div>
            <p>Filter by user</p>
            <select class="select select-bordered w-full max-w-xs" bind:value={selectedUser} on:change={filter}>
              <option value={null}>All</option>
              {#each [...new Set(predictions.map(prediction => prediction.user))] as user}
                <option value={user}>{user}</option>
              {/each}
            </select>
        </div>
        <div>
            <p>Filter by duration</p>
            <select class="select select-bordered w-full max-w-xs" bind:value={filterDuration} on:change={filter}>
              {#each Object.keys(timeFilters) as duration}
                <option value={duration}>{duration}</option>
              {/each}
            </select>
        </div>
        
    </div>
    <div>
        {#if predictions.length === 0}
        <p>Loading...</p>
      {:else}
      <div class="h-[300px] p-4 border rounded group">
        <Chart
          data={filteredPredictions}
          x="finished"
          xScale={scaleBand().padding(0.4)}
          y="duration"
          yDomain={[0, null]}
          yNice={4}
          padding={{ left: 16, bottom: 24 }}
          tooltip={{ mode: "band" }}
        >
          <Svg>
            <Axis placement="left" grid rule />
            
            <Bars
              radius={4}
              strokeWidth={1}
              class="fill-primary group-hover:fill-gray-300 transition-colors"
            />
            <Highlight area>
              <svelte:fragment slot="area" let:area>
                <RectClipPath
                  x={area.x}
                  y={area.y}
                  width={area.width}
                  height={area.height}
                  spring
                >
                  <Bars 
                    radius={4} 
                    strokeWidth={1} 
                    class="fill-primarr" 
                    color="green"
                  />
                </RectClipPath>
              </svelte:fragment>
            </Highlight>
          </Svg>
          <Tooltip header={(data) => data.user} let:data>
            <TooltipItem label="User" value={data.user} />
            <TooltipItem label="Date" value={data.finished} />
            <TooltipItem label="duration" value={data.duration} />
            <TooltipItem label="Status" value={data.status} />
          </Tooltip>
        </Chart>
      </div>
  
      <div class="overflow-x-auto border rounded-md mt-4">
          <table class="table table-xs">
            <thead>
              <tr>
                  <th>Status</th> 
                  <th>User</th> 
                  <th>Image</th> 
                  <th>Date</th> 
                  <th>duration</th> 
              </tr>
            </thead> 
            <tbody>
              {#each filteredPredictions as prediction}
                <tr>
                  <td>
                      {#if prediction.status === 'succeeded'}
                          <div class="bg-green-500 rounded-full w-2 h-2"></div>
                      {:else if prediction.status === 'failed'}
                          <div class="bg-red-500 rounded-full w-2 h-2"></div>
                      {:else}
                          <div class="bg-gray-500 rounded-full w-2 h-2"></div>
                      {/if}
                  </td>
                  <td>{prediction.user}</td>
                  <td>{prediction.image}</td>
                  <td>{prediction.finished}</td>
                  <td>{prediction.duration}</td>
                </tr>
              {/each}
            </tbody> 
          </table>
        </div>
        {/if}
    </div>

    <!-- Open the modal using ID.showModal() method -->
    <dialog id="token_modal" class="modal">
    <div class="modal-box flex flex-col justify-center">
        <h3 class="font-bold text-lg">Enter your token</h3>
        <div class="space-x-2 mt-2">
            <input class="input input-bordered w-full max-w-xs" type="text" bind:value={token} />
            <button class="btn" on:click={() => setToken(token)}>Submit</button>
        </div>
    </div>
    <form method="dialog" class="modal-backdrop">
        <button>close</button>
    </form>
    </dialog>
  </section>
  
  