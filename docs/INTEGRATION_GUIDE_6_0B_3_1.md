# Integration Guide — Release 6.0B.3.1

The installer:

1. verifies the exact baseline HEAD;
2. refuses unrelated working-tree changes;
3. writes the universal scoring files;
4. bumps the Streamlit official-score cache schema;
5. compiles changed Python modules;
6. runs the new cross-domain tests plus existing Release 5 scoring tests;
7. runs `git diff --check`;
8. does not commit or push.

After installation, restart Streamlit and upload the HRIS documents again.
The cache-schema change prevents reuse of the prior 30/30/30/29 session.
