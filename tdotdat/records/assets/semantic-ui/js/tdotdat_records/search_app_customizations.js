/*
 *   Copyright (C) 2022 TDoTP.
 *
 * TDotDat is free software; you can redistribute it and/or modify it under
 * the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import { Input, Item, List, Checkbox, Card, Form, Button, Grid } from "semantic-ui-react";
import { SearchBar } from "react-searchkit";


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
  console.log("list item: ", result, index);

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
