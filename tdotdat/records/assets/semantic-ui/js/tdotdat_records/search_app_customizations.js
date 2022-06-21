/*
 *   Copyright (C) 2022 TDoTP.
 *
 * TDotDat is free software; you can redistribute it and/or modify it under
 * the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import { Input } from "semantic-ui-react";

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


