# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Literal

from pydantic import Field

from data_designer.config.dataset_builders import BuildStage
from data_designer.config.processors import ProcessorConfig


class RegexFilterProcessorConfig(ProcessorConfig):
    """Filter rows based on regex matching on a column.

    Typically used as a PRE_GENERATION processor to filter seed data.
    """

    processor_type: Literal["regex-filter"] = "regex-filter"
    column: str = Field(description="Column to apply regex filter on")
    pattern: str = Field(description="Regex pattern to match")
    invert: bool = Field(default=False, description="If True, keep rows that do NOT match")
    build_stage: BuildStage = BuildStage.PRE_GENERATION
