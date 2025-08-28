def get_html():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>BKK Routes Dashboard</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
        }

        header {
            margin-bottom: 20px;
        }

        #chartWrapper {
            display: flex;
            justify-content: center;
        }

        #chartContainer {
            width: 80vw;
            height: 80vh;
        }
    </style>
</head>
<body>
    <header>
        <h1>BKK Routes Dashboard</h1>
        <label for="routeSelect">Choose a route:</label>
        <select id="routeSelect"></select>
    </header>

    <div id="chartWrapper">
        <div id="chartContainer"></div>
    </div>

    <script type="module">
    import Vizzu from 'https://cdn.jsdelivr.net/npm/vizzu@0.17/dist/vizzu.min.js';

    let chart = new Vizzu('chartContainer');

    async function loadRoutes() {
        const resp = await fetch('/routes');
        const data = await resp.json();
        const select = document.getElementById('routeSelect');
        data.routes.forEach(route => {
            const option = document.createElement('option');
            option.value = route;
            option.text = route;
            select.appendChild(option);
        });

        if (data.routes.length > 0) {
            const firstRoute = data.routes[0];
            select.value = firstRoute;
            loadStats(firstRoute);
        }
    }

    async function loadStats(routeId) {
        const resp = await fetch('/route/' + routeId);
        const apiData = await resp.json();

        const vizzuData = await fetch('/transform/' + routeId).then(r => r.json());

        chart.feature('tooltip', true);

        chart.animate({
            data: vizzuData,
            config: {
                x: ["Day", "Period"],
                y: "Deviation(min) from avg",
                color: "Period"
            },
            style: {
                legend: {
                    width: "15em"
                }
            }
        });
    }

    document.getElementById('routeSelect').addEventListener('change', (e) => {
        loadStats(e.target.value);
    });

    loadRoutes();
    </script>
</body>
</html>
"""
