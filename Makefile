PROJECTNAME=shenzhen_solitaire

.PHONY: test coverage typing linting

test:
	python -m unittest discover

coverage:
	coverage run -m unittest discover && coverage report --skip-covered

typing:
	mypy --strict ${PROJECTNAME} test

linting:
	pylint --extension-pkg-whitelist=cv2 ${PROJECTNAME} test
