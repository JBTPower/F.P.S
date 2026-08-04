import streamlit as st


def render(storage):
    category_key = "team_builder"
    category_label = storage.get_category_label(category_key)

    st.header(category_label)
    st.caption(f"Default folder: {category_label}")
    st.write("Create or remove classes for team planning and rotations.")

    _render_new_class_panel(storage, category_key, category_label)
    st.divider()
    _render_existing_classes(storage, category_key)


def _render_new_class_panel(storage, category_key: str, category_label: str):
    with st.expander("Add a new class", expanded=True):
        new_name = st.text_input(
            "Class name",
            placeholder="Enter a new class name",
            key=f"new_class_name_{category_key}",
        )
        if st.button("Create class", key=f"create_class_{category_key}"):
            success, result = storage.add_class(new_name, category_key)
            if success:
                st.success(f"Created class '{result['name']}' in {category_label}.")
                st.experimental_rerun()
            else:
                st.error(result)


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
