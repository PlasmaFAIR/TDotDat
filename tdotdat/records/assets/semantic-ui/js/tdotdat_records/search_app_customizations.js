/*
 *   Copyright (C) 2022 TDoTP.
 *
 * TDotDat is free software; you can redistribute it and/or modify it under
 * the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import { Input, Item, List, Checkbox, Card, Form, Button, Grid } from "semantic-ui-react";
import { SearchBar } from "react-searchkit";
import axios from 'axios';


export const TDotDatSearchBarElement = ({
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
          color: "orange",
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

export const TDotDatResultsListItem = ({ result, index }) => {
  const contributors = result.metadata.contributors || [];

  return (
    <Item key={index}>
      <Item.Content>
        <Item.Header href={`/records/${result.id}`}>{result.metadata.title}</Item.Header>
        <Item.Description>
          <p>Run with <b>{result.metadata.software.name}</b></p>
          {contributors && (
            <List horizontal relaxed>
              {contributors.map((contributor, idx) => (
                <List.Item key={idx}>{contributor.name}</List.Item>
              ))}
            </List>
          )}
        </Item.Description>
        <Item.Extra>
          <Checkbox
              label="select"
              name='recordResultItem'
              value={`${result.id}`}
          />
        </Item.Extra>
      </Item.Content>
    </Item>
  );
};

export const TDotDatResultsGridItem = ({ result, index }) => {
  const contributors = result.metadata.contributors || [];
  return (
    <Card fluid key={index} href={`/records/${result.id}`}>
      <Card.Content>
        <Card.Header>{result.metadata.title}</Card.Header>
        <Card.Description>
          {contributors && (
            <List horizontal relaxed>
              {contributors.map((contributor, idx) => (
                <List.Item key={idx}>{contributor.name}</List.Item>
              ))}
            </List>
          )}
        </Card.Description>
      </Card.Content>
    </Card>
  );
};

export const TDotDatSearchBarContainer = () => {

  // Collect all the selected records and compare them
  const handleDownloadSelected = (event, data) => {
    event.preventDefault();

    const checkboxes = document.getElementsByName('recordResultItem');
    const selected = Array.from(checkboxes).filter((checkbox) => checkbox.checked);

    if (selected.length == 0) return;

    const values = selected.map((checkbox) => checkbox.value).join(",");
    window.location.href = "/records/compare/" + values;
  };

  // Get all the IDs for the current search
  const getAllIds = (url, data = []) => {
    return axios.get(url)
      .then((response) => {
        data.push(...response.data.hits.hits.map(hit => hit.id));
        if (!response.data.links.next) return data;
        return getAllIds(response.data.links.next, data);
      })
  };

  // Get all the PIDs of the records in the search and compare them
  const handleDownloadAll = (event, data) => {
    event.preventDefault();
    // Handily, the Invenio search app stores the current query state
    // in the page url, which we can extract and use to make the same
    // search to the REST API
    const search_url = "/api/records/" + window.location.search;

    getAllIds(search_url).then(ids => {
      const compare_url = "/records/compare/" + ids.join(",");
      window.location.href = compare_url;
    });
  };

  // Plot search results
  const plotSearch = (event, data) => {
    event.preventDefault();
    window.location.href ="/records/plot" + window.location.search
  }

  return (
    <Form>
      <Grid relaxed padded>
        <Grid.Row columns={2}>
          <Grid.Column width={4} />
          <Grid.Column width={8}>
            <Button type="submit" onClick={handleDownloadAll} primary>Compare all</Button>
            <Button type="submit" onClick={handleDownloadSelected} secondary>Compare selected</Button>
            <Button type="submit" onClick={plotSearch} secondary>Plot all</Button>
          </Grid.Column>
        </Grid.Row>
      </Grid>
    </Form>
  )
};
