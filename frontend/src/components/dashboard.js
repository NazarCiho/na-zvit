import React from "react";
import { render } from "react-dom";
import moment from "moment";
import { AdvancedChart, TickerTape, TechnicalAnalysis, CompanyProfile, SingleTicker } from "react-tradingview-embed";

import {
  XYPlot,
  Hint,
  LineSeries,
  FlexibleXYPlot,
  VerticalBarSeries,
  VerticalGridLines,
  HorizontalGridLines,
  XAxis,
  YAxis,
  AreaSeries
} from "react-vis";

var formatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD"
});

class Dashboard extends React.Component {
  constructor(props) {
    super(props);
  }

  state = {
    times: [],
    high: [],
    low: [],
    chartData: [],
    query: "BTC",
    leaderboard: [],
    addressData: "",
    symbol: ""
  };

  componentDidMount() {
    this.loadChartData();
  }

  loadChartData = async () => {
    const response = await fetch(
      `https://min-api.cryptocompare.com/data/blockchain/histo/day?fsym=${this.state.query}&api_key=54c69a67adfc783963d3589c5a08a40a5d619b0f22b94b1c79df9acc9129c5ff&limit=30`
    );
    const data = await response.json();
    const bulkData = data.Data.Data;
    const dataArray = [];
    {
      bulkData.map((y) =>
        dataArray.push({
          x: y.time * 1000,
          y: y.transaction_count * y.average_transaction_value
        })
      );
    }
    this.setState({ chartData: dataArray });
    this.setState({ symbol: this.state.query });
  };

  handleInputChange = () => {
    this.setState({
      query: this.search.value
    });
  };
  render() {
    const { chartData, query, addressData, symbol } = this.state;

    return (
      <div>
        <div className="inputDiv">
          <input
            placeholder="Search for a symbol"
            ref={(input) => (this.search = input)}
            onChange={this.handleInputChange}
            className="dataRequest"
          />
          <button onClick={this.loadChartData} className="dataRequest">
            Load Onchain Data
          </button>

          <TickerTape
              widgetProps={{
              showSymbolLogo: true,
              isTransparent: false,
              displayMode: "adaptive",
              colorTheme: "dark",
              autosize: true,


            }}
          />
          <SingleTicker
              widgetProps={{
              symbol: query + "USD",
              width: 250,
              isTransparent: false,
              colorTheme: "dark",
              locale: "en",

            }}
          />
        </div>

        <div className="charty">
          {query.length > 2 ? (
            <AdvancedChart
                widgetProps={{
                interval: "1",
                style: "1",
                colorTheme: "dark",
                timezone: "Europe/Athens",
                backgroundColor:"rgb(16, 16, 20)",
                allow_symbol_change: true,
                width: "60%",
                symbol: query + "USD",
              }}
            />
          ) : (
            "BTCUSD"
          )}

          <div className="taChart">
            {query.length > 2 ? (
              <TechnicalAnalysis
                  widgetProps={{
                  interval: "1D",
                  colorTheme: "dark",
                  width: "100%",
                  symbol: query + "USD"
                }}
              />
            ) : (
              query
            )}


          </div>
        </div>

        {chartData.map((x) => (
          <Chart
            key={x.x}
            time={x.x}
            symbol={x.key}
            active_addresses={x.y}
          />
        ))}
      </div>
    );
  }
}

const Chart = (props) => {
  return (
    <div>
      <div className="chart">
      </div>
    </div>
  );
};

const Leader = (props) => {
  return (
    <div className="leaderItem">
      <a href={props.url} target="#">
        <img src={props.logo} alt={props.symbol} className="logo" />
      </a>
      <p className="leaderText">{props.symbol}</p>
      <p className="leaderText">{props.price}</p>
    </div>
  );
};

export default Dashboard;
