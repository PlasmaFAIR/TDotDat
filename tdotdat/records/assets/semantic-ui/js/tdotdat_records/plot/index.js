import React from "react";
import Plot from "react-plotly.js";
import { Grid, Input, Label } from 'semantic-ui-react'
import { createSearchAppInit } from "@js/invenio_search_ui";
import { withState } from "react-searchkit";

export const Results = ({ currentResultsState = {} }) => {
  const { total, hits } = currentResultsState.data;

  var growth_rate = new Array;
    hits.forEach(hit => (
        hit.metadata.wavevector.forEach(wavevector => {
            growth_rate.push(wavevector.eigenmode[0].growth_rate_norm)
        })
    ));

  var ky = new Array;
    hits.forEach(hit => (
        hit.metadata.wavevector.forEach(wavevector => (
            ky.push(wavevector.binormal_component_norm)
        ))
    ));

    console.log(ky, growth_rate);

  return (
    <Grid relaxed>
      <Grid.Row columns={2} width={12}>
        <Grid.Column width={4}>
            Total simulations: <Label color="blue">{total}</Label>
        </Grid.Column>
        <Grid.Column width={8}>
            Search above to change plot data
        </Grid.Column>
      </Grid.Row>
      <Grid.Row>
        <Plot
            data={[
              {
                x: ky,
                y: growth_rate,
                type: 'scatter',
                mode: 'markers',
              },
            ]}
            layout={ {xaxis: {title: {text: "ky"}}, yaxis: {title: {text: "growth rate"}}} }
        />
       </Grid.Row>
    </Grid>
  );
}

const OnResults = withState(Results);

export const TDotDatPlotSearchElement = ({
  placeholder: passedPlaceholder,
  queryString,
  onInputChange,
  executeSearch,
}) => {
  const placeholder = passedPlaceholder || "Search";
  const onBtnSearchClick = () => {
    executeSearch();
  };
  const onKeyPress = (event) => {
    if (event.key === "Enter") {
      executeSearch();
    }
  };
  return (
    <Input
        action={{
          icon: "search",
          onClick: onBtnSearchClick,
          color: "green",
          className: "invenio-theme-search-button",
        }}
        placeholder={placeholder}
        onChange={(event, { value }) => {
          onInputChange(value);
        }}
        value={queryString}
        onKeyPress={onKeyPress}
    />
  );
};

const initSearchApp = createSearchAppInit({
  "ResultsList.item": () => null,
  "ResultsGrid.item": () => null,
  "SearchBar.element": TDotDatPlotSearchElement,
  "SearchApp.resultsPane": OnResults,
  "SearchApp.resultOptions": () => null,
});
