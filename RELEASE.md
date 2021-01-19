- To release a new version of ipyigv on PyPI:

* To release a new version is recommended to build ts dependencies with yarn.

* Make sure to update the `pyproject.toml` with any new dependencies you include in this package.

Update \_version.py
git add the \_version.py file and git commit


```
python setup.py sdist upload
python setup.py bdist_wheel upload
git tag -a X.X.X -m 'comment'
```

git add and git commit
git push
git push --tags

- To release a new version of ipyigv on NPM:

Update `js/package.json` with new npm package version

```
# clean out the `dist` and `node_modules` directories
git clean -fdx
yarn install
yarn publish
```
