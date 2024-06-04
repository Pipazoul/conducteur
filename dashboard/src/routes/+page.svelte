<script lang="ts">
    import { Area, Axis, Chart, Highlight, LinearGradient, RectClipPath, Svg, Tooltip } from "layerchart";
    import { onMount } from "svelte";
  
    interface Prediction {
      user: string;
      image: string;
      status: string;
      started: string; // YYYY-MM-DD HH:MM:SS
      finished: string; // YYYY-MM-DD HH:MM:SS
      duration: number;
    }
  
    let predictions: Prediction[] = [];
    let filteredPredictions: Prediction[] = [];
    let filterDuration = '1h'; // Default filter
    let selectedUser: string | null = null;
  
    const timeFilters = {
      '1h': 1,
      '2h': 2,
      '4h': 4,
      '6h': 6,
      '12h': 12,
      '24h': 24
    };
  
    onMount(() => {
      getPredictions();
      filteredPredictions = predictions;
      // setInterval(getPredictions, 1000); // Uncomment for periodic updates
    });
  
    async function getPredictions() {
      try {
        const response = await fetch("http://localhost:8000/predictions");
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        predictions = data;
        } catch (error) {
            console.error(error);
        }
    }
  
    function filter() {
        const now = new Date();
        // Filter by time
        filteredPredictions = predictions.filter(prediction => {
          const finished = new Date(prediction.finished);
          const diff = (now.getTime() - finished.getTime()) / 1000 / 60 / 60;
          return diff <= timeFilters[filterDuration];
        });
    }

    $: {
        console.log(predictions);
        console.log(filteredPredictions);
    }


  </script>
  
  <section>
    <h1>Predictions Page</h1>
    <select bind:value={filterDuration} on:change={filter}>
      {#each Object.keys(timeFilters) as time}
        <option value={time}>{time}</option>
      {/each}
    </select>
  
    <select bind:value={selectedUser} on:change={filter}>
      <option value={null}>All Users</option>
      {#each Array.from(new Set(predictions.map(p => p.user))) as user}
        <option value={user}>{user}</option>
      {/each}
    </select>
  
    <div class="h-[300px] border rounded">
        <Chart
          data={predictions}
          x="finished"
          y="duration"
          yDomain={[0, null]}
          yNice
          padding={{ top: 48, bottom: 24 }}
          tooltip={{ mode: "bisect-x" }}
          let:width
          let:height
          let:padding
          let:tooltip
        >
          <Svg>
            <LinearGradient class="from-primary/50 to-primary/0" vertical let:url>
              <Area
                line={{ class: "stroke-2 stroke-primary opacity-20" }}
                fill={url}
              />
              <RectClipPath
                x={0}
                y={0}
                width={tooltip.data ? tooltip.x : width}
                {height}
                spring
              >
                <Area line={{ class: "stroke-2 stroke-primary" }} fill={url} />
              </RectClipPath>
            </LinearGradient>
            <Highlight
              points
              lines={{ class: "stroke-primary [stroke-dasharray:unset]" }}
            />
            <Axis placement="bottom" />
          </Svg>
      
          <Tooltip
            y={48}
            xOffset={4}
            variant="none"
            class="text-sm font-semibold text-primary leading-3"
            let:data
          >
            {data.duration} minutes
          </Tooltip>
      
          <Tooltip
            x={4}
            y={4}
            variant="none"
            class="text-sm font-semibold leading-3"
            let:data
          >
            {data.user}
          </Tooltip>
      
          <Tooltip
            x="data"
            y={height + padding.top + 2}
            anchor="top"
            variant="none"
            class="text-sm font-semibold bg-primary text-primary-content leading-3 px-2 py-1 rounded whitespace-nowrap"
            let:data
          >
            {data.finished}
          </Tooltip>
        </Chart>
      </div>
  </section>
  
  <style>
    .chart-container {
      width: 100%;
      height: 300px;
    }
  </style>
  