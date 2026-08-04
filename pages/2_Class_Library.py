import io
from pathlib import Path

import streamlit as st


def render(storage):
    category_key = "class_library"
    category_label = storage.get_category_label(category_key)

    st.header(category_label)
    st.caption(f"Default folder: {category_label}")
    st.write(
        "Upload class materials into course folders for PDFs, PPTs, and documents so Felipe can build a growing library over time."
    )

    classes = storage.get_classes(category_key)
    _render_new_class_panel(storage, category_key, category_label)
    st.divider()
    _render_class_upload_panel(storage, classes)
    st.divider()
    _render_existing_classes(storage, category_key)


def _render_new_class_panel(storage, category_key: str, category_label: str):
    with st.expander("Create a new class folder", expanded=True):
        new_name = st.text_input(
            "Class name",
            placeholder="Enter a new class name for Class Material Library",
            key=f"new_class_name_{category_key}",
        )
        if st.button("Create class", key=f"create_class_{category_key}"):
            success, result = storage.add_class(new_name, category_key)
            if success:
                st.success(f"Created class '{result['name']}' in {category_label}.")
                st.experimental_rerun()
            else:
                st.error(result)


def _render_class_upload_panel(storage, classes):
    st.subheader("Upload class documents")
    if not classes:
        st.warning("Create a class folder first before uploading materials.")
        return

    class_options = {item["name"]: item["id"] for item in classes}
    default_class_name = classes[0]["name"] if classes else ""
    selected_name = st.selectbox(
        "Select a class folder",
        list(class_options.keys()),
        index=0,
        key="selected_library_class",
    )
    class_id = class_options[selected_name]

    uploaded_file = st.file_uploader(
        "Upload course materials",
        type=["pdf", "ppt", "pptx", "docx", "txt", "md"],
        key="class_material_upload",
    )

    if uploaded_file is not None:
        if st.button("Save uploaded document", key="save_uploaded_material"):
            content = uploaded_file.read()
            success, result = storage.upload_file(
                class_id,
                uploaded_file.name,
                content,
                uploaded_file.type or "application/octet-stream",
            )
            if success:
                st.success(f"Saved {uploaded_file.name} in {selected_name}.")
                st.experimental_rerun()
            else:
                st.error(result)

    files = storage.get_files_for_class(class_id)
    if files:
        st.markdown("**Uploaded files in this class folder:**")
        for file_item in files:
            file_path = Path(storage.data_dir / file_item["path"])
            download_data = file_path.read_bytes() if file_path.exists() else b""
            with st.expander(file_item["name"], expanded=False):
                st.write(f"Type: {file_item.get('mime_type', 'unknown')}")
                if download_data:
                    st.download_button(
                        "Download",
                        data=download_data,
                        file_name=file_item["name"],
                        mime=file_item.get("mime_type", "application/octet-stream"),
                    )
                delete_key = f"delete_file_{file_item['id']}"
                confirm_key = f"confirm_delete_file_{file_item['id']}"
                if st.button("Delete file", key=delete_key):
                    st.session_state[delete_key] = True

                if st.session_state.get(delete_key, False):
                    confirmation = st.text_input(
                        "Type DELETE to confirm file deletion",
                        key=confirm_key,
                    )
                    if st.button("Confirm delete file", key=f"confirm_submit_file_{file_item['id']}"):
                        if confirmation.strip().upper() == "DELETE":
                            success, message = storage.delete_file(file_item["id"])
                            if success:
                                st.success(message)
                                st.experimental_rerun()
                            else:
                                st.error(message)
                        else:
                            st.error("Please type DELETE exactly to confirm deletion.")
    else:
        st.info("No files have been uploaded for this class yet.")


def _render_existing_classes(storage, category_key: str):
    classes = storage.get_classes(category_key)
    if not classes:
        st.info("No classes have been created yet in this folder.")
        return

    for class_item in classes:
        with st.expander(class_item["name"], expanded=False):
            st.write(f"Folder: **{class_item['folder']}**")
            st.write("Use the delete action below to remove this class permanently.")

            delete_key = f"delete_{class_item['id']}"
            confirm_key = f"confirm_delete_{class_item['id']}"
            if st.button("Delete class", key=delete_key):
                st.session_state[delete_key] = True

            if st.session_state.get(delete_key, False):
                confirmation = st.text_input(
                    "Type DELETE to confirm deletion",
                    key=confirm_key,
                )
                if st.button("Confirm deletion", key=f"confirm_submit_{class_item['id']}"):
                    if confirmation.strip().upper() == "DELETE":
                        success, message = storage.delete_class(class_item["id"])
                        if success:
                            st.success(message)
                            st.experimental_rerun()
                        else:
                            st.error(message)
                    else:
                        st.error("Please type DELETE exactly to confirm deletion.")
