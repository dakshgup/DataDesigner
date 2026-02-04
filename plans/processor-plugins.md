# Plan: Processor Plugins with Global Stages

Created: 2026-02-03
Status: Draft

## Goal

Extend the processor system to support global preprocessing (before generation) and postprocessing (after generation) stages, and enable third-party processor plugins via the existing plugin discovery mechanism.

## Success Criteria

- [ ] `PRE_GENERATION` stage runs once on full seed data before batching/generation
- [ ] `POST_GENERATION` stage runs once on final dataset after all batches complete
- [ ] `PluginType.PROCESSOR` enables external processor plugins
- [ ] ProcessorRegistry loads plugins from entry points
- [ ] Demo plugin package demonstrates both preprocessing and postprocessing
- [ ] Existing `POST_BATCH` behavior unchanged

## Implementation Steps

### Step 1: Extend BuildStage Support

Update processor configuration to accept new stages.

- [ ] Add `PRE_GENERATION` and `POST_GENERATION` to `SUPPORTED_STAGES` in processors.py
- [ ] Add unit tests verifying `ProcessorConfig` accepts the new stage values

**Suggestion**: Check if `BuildStage` enum already has these values defined elsewhere before adding.

### Step 2: Update Dataset Builder for Global Stages

Implement the actual execution of processors at the new stages.

- [ ] Add `_run_pre_generation_processors()` method
  - Load full seed dataset before batch loop
  - Apply PRE_GENERATION processors sequentially
  - Replace the seed reader with an in-memory version containing processed data
  - **Suggestion**: Look for existing in-memory seed reader implementations (e.g., `DataFrameSeedReader`)

- [ ] Add `_run_post_generation_processors()` method
  - Load the final combined dataset after all batches complete
  - Apply POST_GENERATION processors sequentially
  - Rewrite the final dataset with processed results
  - **Suggestion**: Check how existing artifact storage handles dataset loading/writing

- [ ] Integrate calls into the `build()` method at appropriate points
- [ ] Add integration tests for both flows

### Step 3: Add Processor Plugin Support

Enable third-party processor plugins through the existing plugin system.

- [ ] Add `PluginType.PROCESSOR` to the plugin types enum
- [ ] Update `discriminator_field` property to return `"processor_type"` for processors
- [ ] Update `ProcessorRegistry` to discover and load processor plugins
  - **Suggestion**: Follow the pattern used for column generator plugins
  - Use string keys for plugin processors (not enum values)

- [ ] Inject plugin processor configs into the `ProcessorConfigT` type union
  - Follow the existing `_types` pattern used for columns and seed sources

**Follow the `_types` Module Pattern**:

The codebase separates base classes from type unions with plugin injection:
- `column_configs.py` (base) → `column_types.py` (union + injection)
- `seed_source.py` (base) → `seed_source_types.py` (union + injection)

Do the same for processors:
- [ ] Keep `processors.py` with base classes and concrete configs
- [ ] Create `processor_types.py` for `ProcessorConfigT` with plugin injection
- [ ] Plugin configs import from `processors.py` (no circular dependency)

**Threading Note**:

If you encounter deadlocks during plugin discovery with nested imports, the `PluginRegistry` may need a reentrant lock (`RLock`) instead of `Lock`.

### Step 4: Create Demo Plugin Package

Create a separate package demonstrating both processor types.

- [ ] Create package structure under `demo/data_designer_demo_processors/`
- [ ] Implement `RegexFilterProcessor` (PRE_GENERATION)
  - Config: column, pattern, invert flag
  - Filters rows based on regex matching
- [ ] Implement `SemanticDedupProcessor` (POST_GENERATION)
  - Config: column, similarity_threshold, model_name
  - Uses embeddings to find and remove similar rows
  - **Suggestion**: Use sentence-transformers with a small model like `all-MiniLM-L6-v2`

- [ ] Configure entry points in `pyproject.toml` under `data_designer.plugins`
- [ ] Add unit tests for each processor
- [ ] Add README with installation and usage examples

**Logging Suppression** (for sentence-transformers):

Sentence-transformers emits progress bars and warnings when loading models. Suppress them:

- Use `transformers.utils.logging.set_verbosity_error()` to suppress info/warning messages
- Use `transformers.utils.logging.disable_progress_bar()` to suppress progress bars
- Pass `show_progress_bar=False` to `model.encode()` for batch encoding

### Step 5: Demo Notebook

Create a simple, short demo that tests all features end-to-end.

- [ ] Use `#%%` cell markers for IDE compatibility
- [ ] Keep the demo minimal - just enough to verify the feature works
- [ ] Include sample seed data with rows to filter (PRE_GENERATION test)
- [ ] Add an LLM column to generate content, use the `openai-text` model
- [ ] Configure both PRE_GENERATION and POST_GENERATION processors
- [ ] **Run the demo and fix any issues** - don't just write it, execute it
- [ ] Verify the output shows filtering and deduplication working

**Important**: The demo must actually run successfully. Test it before considering this step complete.

**API Notes**: Check the docs for correct Data Designer API usage.

### Step 6: Documentation

Update existing documentation to cover new capabilities.

- [ ] Update processor concepts doc with new stages table
- [ ] Update plugins overview to mention processor plugins
- [ ] Include example entry point configuration

## Testing Strategy

- Write tests alongside implementation, not as a separate step
- Use mocks for external dependencies (seed readers, artifact storage)
- For plugin registry tests, create actual mock classes (not Mock objects) to satisfy type validation

## Risks & Considerations

- **Memory usage**: POST_GENERATION holds full dataset in memory
- **Seed data mutation**: PRE_GENERATION modifies seed data before batching
- **Model download**: Embedding models download on first use; perform pre-download on uv install

## Files Modified

Core:
- `packages/data-designer-config/src/data_designer/config/processor_types.py` (new)
- `packages/data-designer-config/src/data_designer/config/processors.py`
- `packages/data-designer-config/src/data_designer/config/data_designer_config.py`
- `packages/data-designer-config/src/data_designer/config/config_builder.py`
- `packages/data-designer-config/src/data_designer/plugin_manager.py`
- `packages/data-designer-config/src/data_designer/plugins/plugin.py`
- `packages/data-designer-config/src/data_designer/plugins/registry.py`
- `packages/data-designer-engine/src/data_designer/engine/dataset_builders/column_wise_builder.py`
- `packages/data-designer-engine/src/data_designer/engine/processing/processors/registry.py`
- `packages/data-designer-engine/src/data_designer/engine/validation.py`

Demo:
- `demo/data_designer_demo_processors/` (new package)

Docs:
- `docs/concepts/processors.md`
- `docs/plugins/overview.md`
