from books import forms


class TestPostBookForm:
    def test_form_valid(self):
        form = forms.PostBookForm(data={})
        assert form.is_valid() is False

        form = forms.PostBookForm(data={"title": "Doughnot Economics"})
        assert form.is_valid() is False

        form = forms.PostBookForm(
            data={
                "title": (
                    "Lorem ipsum dolor sit amet "
                    "consectetur adipisicing elit. "
                    "Asperiores quia corrupti laborum "
                    "veritatis eum. Maiores numquam est "
                    "repellat adipisci porro a fuga, itaque "
                    "de animi, rerum officia minima hic "
                    "necessitatibus?"
                ),
                "author": "Kate Raworth",
            }
        )
        assert form.is_valid() is False

        form = forms.PostBookForm(data={"title": "Hi", "author": "KD"})
        assert form.is_valid() is False

        form = forms.PostBookForm(
            data={"title": "Hi there", "author": "Katja D"}
        )
        assert form.is_valid() is True

        form = forms.PostBookForm(
            data={"title": "Doughnot Economics", "author": "Kate Raworth"}
        )
        assert form.is_valid() is True
