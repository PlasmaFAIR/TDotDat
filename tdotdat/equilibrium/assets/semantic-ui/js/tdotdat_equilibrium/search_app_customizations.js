/*
 *   Copyright (C) 2022 TDoTP.
 *
 * TDotDat is free software; you can redistribute it and/or modify it under
 * the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import { Input, Card, List, Item } from "semantic-ui-react";

export const TDotDatEquilibriumSearchBarElement = ({
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
        color: "red",
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

// Customisation for the grid-view display of results
export const TDotDatEquilibriumResultsGridItem = ({ result, index }) => {
    const contributors = result.metadata.contributors || [];
    return (
      <Card fluid key={index} href={`/equilibrium/${result.id}`}>
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

// Customisation for the list-view display of results
export const TDotDatEquilibriumResultsListItem = ({ result, index }) => {
  const contributors = result.metadata.contributors || [];
  return (
    <Item key={index} href={`/equilibrium/${result.id}`}>
      <Item.Content>
        <Item.Header>{result.metadata.title}</Item.Header>
        <Item.Description>
          {contributors && (
            <List horizontal relaxed>
              {contributors.map((contributor, idx) => (
                <List.Item key={idx}>{contributor.name}</List.Item>
              ))}
            </List>
          )}
        </Item.Description>
      </Item.Content>
    </Item>
  );
};
