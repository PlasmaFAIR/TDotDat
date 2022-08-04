import React from "react";
import Plot from "react-plotly.js";
import { Grid, Input, Label } from 'semantic-ui-react'
import { createSearchAppInit } from "@js/invenio_search_ui";
import { withState } from "react-searchkit";

export const Results = ({ currentResultsState = {} }) => {
  const { total, hits } = currentResultsState.data;

  const temperature = hits.map(hit => hit.metadata.inputs.temperature);
  const q = hits.map(hit => hit.metadata.equilibrium.q);

  return (
    <Grid relaxed>
      <Grid.Row/>
      <Grid.Row columns={2} width={12}>
        <Grid.Column width={4}>
          Total simulations: <Label color="blue">{total}</Label>
        </Grid.Column>
      </Grid.Row>
      <Grid.Row>
        <Plot
            data={[
              {
                x: q,
                y: temperature,
                type: 'scatter',
                mode: 'markers',
              },
            ]}
            layout={ {xaxis: {title: {text: "q"}}, yaxis: {title: {text: "temperature"}}} }
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
