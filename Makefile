
ACTIVATE := source .venv/bin/activate

install:
	which uv || (curl -LsSf https://astral.sh/uv/install.sh | sh)
	uv venv --python 3.13
	uv pip install -r requirements.txt
	rm -f example.db

example.db:
	$(ACTIVATE) && python create_db.py

run: example.db
	@echo You can now run any of the add or query scripts.
	@echo
	ls -1 *.sh
	@echo
	$(ACTIVATE) && python graphql_posts_example.py

clean:
	rm -rf .venv/ example.db

.PHONY: install run clean
