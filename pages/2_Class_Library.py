import io
from pathlib import Path

import streamlit as st


def render(storage, class_id: str):
    st.header("Class Material Library")
    st.write(
        "Organize course documents into module folders. "
        "Upload PDFs, presentations, and notes into each module over time."
    )

    class_item = storage.get_class(class_id)
    modules = storage.get_modules_for_class(class_id)
    selected_module_key = f"selected_material_module_{class_id}"
    module_name_key = f"upload_module_name_{class_id}"

    if selected_module_key not in st.session_state:
        st.session_state[selected_module_key] = modules[0] if modules else ""
    if module_name_key not in st.session_state:
        st.session_state[module_name_key] = st.session_state[selected_module_key]

    selected_module = st.selectbox(
        "Choose a module folder",
        modules,
        index=modules.index(st.session_state[selected_module_key]) if st.session_state[selected_module_key] in modules else 0,
        key=selected_module_key,
    )

    if selected_module != st.session_state[selected_module_key]:
        st.session_state[selected_module_key] = selected_module
        st.session_state[module_name_key] = selected_module

    module_name = st.text_input(
        "Module folder name",
        value=st.session_state[module_name_key],
        key=module_name_key,
    )

    if st.button("Create / select module folder", key=f"create_module_{class_id}"):
        if not module_name.strip():
            st.error("Please enter a module folder name.")
        else:
            success, result = storage.add_module(class_id, module_name.strip())
            if success:
                st.success(f"Module '{module_name.strip()}' is ready.")
                st.session_state[selected_module_key] = module_name.strip()
                try:
                    rerun = getattr(st, "experimental_rerun", None)
                    if callable(rerun):
                        rerun()
                except Exception:
                    try:
                        st.stop()
                    except Exception:
                        pass
            else:
                st.error(result)

    st.divider()

    if not module_name.strip():
        st.warning("Enter a module name to upload or view files.")
        return

    if module_name not in modules:
        modules.append(module_name)

    with st.expander("Upload document to this module", expanded=True):
        uploaded_file = st.file_uploader(
            "Choose a document",
            type=["pdf", "ppt", "pptx", "docx", "txt", "md"],
            key=f"class_material_upload_{class_id}",
        )

        if uploaded_file is not None and st.button("Save uploaded document", key=f"save_uploaded_material_{class_id}"):
            content = uploaded_file.read()
            success, result = storage.upload_file(
                class_id,
                module_name,
                uploaded_file.name,
                content,
                uploaded_file.type or "application/octet-stream",
            )
            if success:
                st.success(f"Saved {uploaded_file.name} in {module_name}.")
                try:
                    rerun = getattr(st, "experimental_rerun", None)
                    if callable(rerun):
                        rerun()
                except Exception:
                    try:
                        st.stop()
                    except Exception:
                        pass
            else:
                st.error(result)

    st.divider()
    st.subheader(f"Files in {module_name}")
    files = storage.get_files_for_class(class_id, module=module_name)
    if not files:
        st.info("No documents uploaded to this module yet.")
        return

    for file_item in files:
        file_path = Path(storage.data_dir / file_item["path"])
        download_data = file_path.read_bytes() if file_path.exists() else b""
        with st.expander(file_item["name"], expanded=False):
            st.write(f"Uploaded: {file_item.get('created_at', 'unknown')}")
            st.write(f"File type: {file_item.get('mime_type', 'unknown')}")
            if download_data:
                st.download_button(
                    "Download",
                    data=download_data,
                    file_name=file_item["name"],
                    mime=file_item.get("mime_type", "application/octet-stream"),
                    key=f"download_{file_item['id']}",
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
                            try:
                                rerun = getattr(st, "experimental_rerun", None)
                                if callable(rerun):
                                    rerun()
                            except Exception:
                                try:
                                    st.stop()
                                except Exception:
                                    pass
                        else:
                            st.error(message)
                    else:
                        st.error("Please type DELETE exactly to confirm deletion.")
