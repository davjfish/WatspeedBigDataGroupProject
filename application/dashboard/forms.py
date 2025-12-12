from django import forms


class FileImportForm(forms.Form):
    file_format = forms.ChoiceField(
        label="In which schema is the file you are going to be uploading?",
        choices=(
            (1, "Emergency - 911 Calls from Montgomery County, PA"),
        )

    )
    temp_file = forms.FileField(
        label="File to import",
        help_text="Please select or drag-and-drop the file to import.",
        widget=forms.FileInput(attrs={'class': "form-control"})
    )
