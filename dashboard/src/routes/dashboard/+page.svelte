<script lang="ts">
    import { Area, Axis, Bars, Chart, Highlight, LinearGradient, RectClipPath, Svg, Tooltip, TooltipItem } from "layerchart";
    import { scaleBand } from "d3-scale";
    import { onMount } from "svelte";
    import {url, token, predictions} from '$lib/store';
	import { getPredictions } from '../../lib/store';
  
    interface Prediction {
      user: string;
      image: string;
      status: string;
      started: string; // YYYY-MM-DD HH:MM:SS
      finished: string; // YYYY-MM-DD HH:MM:SS
      duration: number;
      co2: number;
      request: "asynchronous" | "synchronous";
    }
    
    let filteredPredictions: Prediction[] = [];
    let filterDuration = '6h'; // Default filter
    let selectedUser: string | null = null;



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
  
    $: {
       if($predictions.length > 0) {
           filter();
       }
    }

    function formatDate(dateString) {
      try{
        //split date and time
        const [dateStr, timeStr] = dateString.split(' ');

        //split year-month-date and hours-minutes-seconds
        const [year, month, day] = dateStr.split('-').map(Number);
        const [hours, minutes, seconds] = timeStr.split(':').map(Number);

        //create Date object
        const date = new Date(year, month - 1, day, hours, minutes, seconds);

        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffSec = Math.floor(diffMs / 1000);
        const diffMin = Math.floor(diffSec / 60);
        const diffHr = Math.floor(diffMin / 60);

        if (diffSec < 60) {
            return 'less than 1 min';
        } else if (diffMin < 60) {
            return diffMin + ' min ago';
        } else if (diffHr < 24) {
            return diffHr + ' hours ago';
        } else {
            const outputDay = ("0" + day).slice(-2);
            const outputMonth = ("0" + month).slice(-2);
            const outputYear = year;
            const outputHours = ("0" + hours).slice(-2);
            const outputMinutes = ("0" + minutes).slice(-2);
            return `${outputDay}/${outputMonth}/${outputYear} - ${outputHours}:${outputMinutes}`;
        }
        } catch(err) {
            return
        }
    }

    async function filter() {
        const now = new Date();
        const durationHours = timeFilters[filterDuration]; // Corrected line

        const timeLimit = new Date(now.getTime() - durationHours * 3600 * 1000);

        let userFilteredPredictions = filterByUser();

        // reverse the array to get the latest predictions first
        userFilteredPredictions.reverse();

        filteredPredictions = userFilteredPredictions.filter(prediction => {
            const finishedTime = new Date(prediction.finished);
            return finishedTime && finishedTime > timeLimit;
        });

        // get the pending predictions they have the status pending
        const pendingPredictions = userFilteredPredictions.filter(prediction => prediction.status === 'pending');
        // get running predictions they have the status running
        const runningPredictions = userFilteredPredictions.filter(prediction => prediction.status === 'running');
        filteredPredictions = [...pendingPredictions,...runningPredictions, ...filteredPredictions];
    }

    function filterByUser() {
        if (selectedUser) {
            return $predictions.filter(prediction => prediction.user === selectedUser);
        }
        return $predictions;
    }

    async function deletePrediction(id:string){
      let response = await fetch(`${$url}prediction/${id}`, 
      {method: 'DELETE', 
      headers: {'Authorization': `Bearer ${$token}`}});
      let data = await response.json();
      return data;
    }


  </script>
  
  <section>
    <h1 class="text-2xl uppercase font-bold mb-4">🚊 Conducteur Stats</h1>
    <div class="flex space-x-4 pb-4">
        <div>
            <p>Filter by user</p>
            <select class="select select-bordered w-full max-w-xs" bind:value={selectedUser} on:change={filter}>
              <option value={null}>All</option>
              {#each [...new Set($predictions.map(prediction => prediction.user))] as user}
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
        {#if $predictions.length === 0}
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
            <TooltipItem label="Name" value={data.image.substring(0, 30)+ "..."} />
            <TooltipItem label="Date" value={formatDate(data.finished) || 'N/A'}  />
            <TooltipItem label="duration" value={data.duration} />
            <TooltipItem label="Status" value={data.status} />
          </Tooltip>
        </Chart>
      </div>
  
      <div class="overflow-x-auto border rounded-md mt-4">
          <table class="table table-xs">
            <thead>
              <tr>
                  <th>Type</th> 
                  <th>Status</th> 
                  <th>User</th> 
                  <th>Image</th> 
                  <th>Date</th> 
                  <th>co2 used(g)</th>
                  <th>duration (sec)</th> 
                  <th>Delete</th>
              </tr>
            </thead> 
            <tbody>
              {#each filteredPredictions as prediction}
                <tr>
                  {#if prediction.request === 'asynchronous'}
                    <td>🐌</td>
                  {:else}
                    <td>🏃</td>
                  {/if}
                  <td>
                      {#if prediction.status === 'completed'}
                          <div class="bg-green-500 rounded-full w-2 h-2"></div>
                      {:else if prediction.status === 'pending'}
                        <div class="bg-blue-500 animate-pulse  rounded-full w-2 h-2"></div>
                      {:else if prediction.status === 'running'}
                        <div class="bg-orange-500 animate-pulse  rounded-full w-2 h-2"></div>
                      {:else if prediction.status === 'failed'}
                          <div class="bg-red-500 rounded-full w-2 h-2"></div>
                      {:else}
                          <div class="bg-gray-500 rounded-full w-2 h-2"></div>
                      {/if}
                  </td>
                  <td>{prediction.user}</td>
                  <td>{prediction.image?.split('@')[0] || prediction.image }</td>
                  <td>{formatDate(prediction.finished) || "No date"}</td>
                  <td>{prediction.co2 || 0}</td>
                  <td>{prediction.duration || 0}</td>
                  <td><button on:click={deletePrediction(prediction.id)} >❌</button></td>
                </tr>
              {/each}
            </tbody> 
          </table>
        </div>
        {/if}
    </div>
  </section>
  
  